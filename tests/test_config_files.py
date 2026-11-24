"""Exercise actual file/transfer code with ArduinoJson and an in-memory FS.

Run: python3 tests/test_config_files.py [ArduinoJson/src]
No ESP, network, flash writes or package downloads. This cannot prove actual
LittleFS power-loss behavior or timestamps on hardware.
"""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
JSON = Path(sys.argv[1]) if len(sys.argv) > 1 else next(
    (ROOT.parent/'ESP32-Jarolift-Controller/.pio/libdeps').glob('*/ArduinoJson/src'))

FS = r'''
#pragma once
#include <algorithm>
#include <cstdint>
#include <cstring>
#include <ctime>
#include <functional>
#include <map>
#include <string>
constexpr auto FILE_READ = "r", FILE_WRITE = "w";
struct File {
  std::string *data = nullptr;
  size_t offset = 0;
  bool shortWrite = false;
  explicit operator bool() const { return data; }
  size_t size() const { return data ? data->size() : 0; }
  int available() { return size() - offset; }
  int read() { return available() ? uint8_t((*data)[offset++]) : -1; }
  size_t readBytes(char *buffer, size_t size) { return read(reinterpret_cast<uint8_t *>(buffer), size); }
  size_t read(uint8_t *buffer, size_t count) {
    count = std::min(count, size() - offset);
    memcpy(buffer, data->data() + offset, count); offset += count; return count;
  }
  size_t write(const uint8_t *buffer, size_t count) {
    if (shortWrite && count) --count;
    data->append(reinterpret_cast<const char *>(buffer), count); return count;
  }
  void close() { data = nullptr; }
  void flush() {}
  time_t getLastWrite() { return 1795554000; }
};
struct FakeFS {
  std::map<std::string, std::string> files;
  size_t capacity = 131072;
  bool shortWrite = false, failRename = false, failOpen = false;
  size_t totalBytes() { return capacity; }
  size_t usedBytes() { size_t result = 0; for (auto &f : files) result += f.second.size(); return result; }
  bool exists(const char *path) { return files.count(path); }
  File open(const char *path, const char *mode) {
    if (!strcmp(mode, "w")) {
      if (failOpen) return {};
      files[path].clear(); return {&files[path], 0, shortWrite};
    }
    return files.count(path) ? File{&files[path]} : File{};
  }
  bool remove(const char *path) { return files.erase(path); }
  bool rename(const char *from, const char *to) {
    if (failRename || !files.count(from)) return false;
    files[to] = files[from]; files.erase(from); return true;
  }
};
inline FakeFS LittleFS;
'''

WEB = r'''
#pragma once
#include <ArduinoJson.h>
#include <LittleFS.h>
#include <atomic>
#include <cstdlib>
using String = std::string;
constexpr int HTTP_POST = 1, HTTP_GET = 2;
struct FakeResponse {
  std::string path, cache;
  bool download;
  void addHeader(const char *, const char *value) { cache = value; }
};
struct AsyncWebServerRequest {
  void *_tempObject = nullptr;
  File _tempFile;
  bool authenticated = true;
  int status = 0;
  std::string responsePath, responseBody, cache;
  bool download = false;
  size_t length = 100;
  std::function<void()> disconnected;
  ~AsyncWebServerRequest() { if (disconnected) disconnected(); free(_tempObject); }
  size_t contentLength() { return length; }
  void onDisconnect(std::function<void()> callback) { disconnected = callback; }
  void send(int code, const char *, const String &) { status = code; }
  FakeResponse *beginResponse(FakeFS &, const char *path, const char *, bool attachment) { return new FakeResponse{path, "", attachment}; }
  void send(FakeResponse *response) {
    status = 200; responsePath = response->path; download = response->download; cache = response->cache;
    responseBody = LittleFS.files[responsePath]; delete response;
  }
};
struct Server {
  std::function<void(AsyncWebServerRequest *)> download;
  template<typename A> void on(const char *, int, A callback) { download = callback; }
  std::function<void(AsyncWebServerRequest *)> finish;
  std::function<void(AsyncWebServerRequest *, const String &, size_t, uint8_t *, size_t, bool)> chunk;
  template<typename A, typename B> void on(const char *, int, A a, B b) { finish = a; chunk = b; }
};
struct EspWebUI {
  enum uploadStatus { UPLOAD_BEGIN, UPLOAD_FINISH, UPLOAD_ERROR };
  const char *configFileSection = "jaro";
  bool (*callbackConfigFileReady)() = nullptr;
  void (*callbackUpload)(uploadStatus, const char *) = nullptr;
  std::atomic<bool> configFileBusy{false}, configUploadPending{false};
  Server server;
  std::string lastResult;
  void sendWs(JsonDocument &doc) { lastResult = doc["result"] | ""; }
  bool isAuthenticated(AsyncWebServerRequest *r) { return r->authenticated; }
  void processConfigUpload();
  void sendConfigFileStatus(const char *result = nullptr, const char *area = nullptr);
  bool handleConfigFileCommand(const char *, const char *);
  void setupConfigUploadRoute();
};
'''

MAIN = r'''
#include "EspWebUI.h"
#include "config_files.h"
#include <cassert>
using namespace EspConfigFiles;
const std::string original = R"({"version":8,"jaro":{"serial":123,"ch_name":["Küche"]},"wifi":{"ssid":"test"}})";
const std::string replacement = R"({"version":8,"jaro":{"serial":456}})";
int restarts = 0;
void restored(EspWebUI::uploadStatus state, const char *) { if (state == EspWebUI::UPLOAD_FINISH) ++restarts; }
bool notReady() { return false; }
void reset() { LittleFS = FakeFS{}; LittleFS.files[active] = original; }
void receive(EspWebUI &ui, AsyncWebServerRequest &request, std::string body, bool final = true, size_t index = 0) {
  ui.server.chunk(&request, "arbitrary-name.json", index, reinterpret_cast<uint8_t *>(body.data()), body.size(), final);
}
int main() {
  reset();
  assert(valid(active, "jaro") && !valid(active, "km271"));
  for (auto body : {"[]", "null", "{}", "{\"jaro\":null}", "{\"jaro\":[]}", "{\"jaro\":true}",
                    "{\"km271\":{}}", "{\"jaro\":{}} garbage", "{\"jaro\":{", "{\"jaro\":{},\"x\":[1,}"}) {
    LittleFS.files[upload] = body;
    assert(!valid(upload, "jaro"));
  }
  LittleFS.files[upload] = "{\"jaro\":{}} \n\t";
  assert(valid(upload, "jaro"));
  assert(copy(active, backup, "jaro") == nullptr);
  assert(LittleFS.files[backup] == original && LittleFS.files[active] == original);
  LittleFS.files[active] = replacement;
  assert(copy(backup, active, "jaro") == nullptr);
  assert(LittleFS.files[active] == original && LittleFS.files[backup] == original);
  for (int fault = 0; fault < 4; ++fault) {
    reset(); LittleFS.files[backup] = replacement;
    if (fault == 0) LittleFS.shortWrite = true;
    if (fault == 1) LittleFS.failRename = true;
    if (fault == 2) LittleFS.failOpen = true;
    if (fault == 3) LittleFS.capacity = 100;
    assert(copy(active, backup, "jaro"));
    assert(LittleFS.files[active] == original && LittleFS.files[backup] == replacement);
  }
  reset();
  EspWebUI ui;
  ui.callbackUpload = restored;
  ui.setupConfigUploadRoute();
  {
    AsyncWebServerRequest missing, unauthorized, exported;
    ui.server.download(&missing);
    assert(missing.status == 404);
    LittleFS.files[backup] = replacement;
    unauthorized.authenticated = false;
    ui.server.download(&unauthorized);
    assert(unauthorized.status == 401);
    ui.server.download(&exported);
    assert(exported.status == 200 && exported.responsePath == backup && exported.download);
    assert(exported.responseBody == replacement && exported.cache == "no-store");
    assert(LittleFS.files[active] == original && LittleFS.files[backup] == replacement);
  }
  {
    AsyncWebServerRequest request;
    receive(ui, request, replacement, false);
    assert(ui.configFileBusy && LittleFS.files[active] == original);
    ui.handleConfigFileCommand("config_files", "backup");
    assert(ui.lastResult == "config_files_busy");
  }
  assert(!ui.configFileBusy && !LittleFS.exists(upload) && LittleFS.files[active] == original);
  for (auto body : {std::string("{\"km271\":{}}"), replacement}) {
    AsyncWebServerRequest request;
    receive(ui, request, body);
    ui.server.finish(&request);
    assert(request.status == 202 && LittleFS.files[active] == original);
    ui.processConfigUpload();
    assert(!ui.configFileBusy);
    if (body == replacement) assert(LittleFS.files[active] == replacement && restarts == 1);
    else assert(LittleFS.files[active] == original && ui.lastResult == "config_files_invalid" && restarts == 0);
  }
  // Second simultaneous request cannot disturb the first one's file/ownership.
  reset();
  {
    AsyncWebServerRequest first, second;
    receive(ui, first, replacement, false);
    receive(ui, second, "broken"); ui.server.finish(&second);
    assert(second.status == 400 && ui.configFileBusy);
    assert(LittleFS.files[upload] == replacement);
  }
  assert(!ui.configFileBusy);
  // Failed writes, malformed multipart, unauthenticated uploads and busy commit.
  for (int fault = 0; fault < 6; ++fault) {
    reset();
    {
      AsyncWebServerRequest request;
      if (fault == 0) LittleFS.shortWrite = true;
      if (fault == 1) request.authenticated = false;
      if (fault == 2) LittleFS.capacity = 100;
      receive(ui, request, replacement);
      if (fault == 3) receive(ui, request, replacement); // second file
      if (fault == 4) LittleFS.failRename = true;
      if (fault == 5) ui.callbackConfigFileReady = notReady;
      ui.server.finish(&request);
      ui.processConfigUpload();
      assert(LittleFS.files[active] == original);
    }
    assert(!ui.configFileBusy);
    ui.callbackConfigFileReady = nullptr;
  }
  reset();
  ui.configFileSection = "km271";
  LittleFS.files[active] = "{\"km271\":{\"use_hc1\":true}}";
  assert(ui.handleConfigFileCommand("config_files", "backup"));
  assert(ui.lastResult == "config_files_created");
  assert(LittleFS.files[active] == LittleFS.files[backup]);
}
'''

with tempfile.TemporaryDirectory(prefix='esp-config-files-') as temp:
    work = Path(temp)
    (work/'LittleFS.h').write_text(FS)
    (work/'EspWebUI.h').write_text(WEB)
    (work/'config_files.h').write_text((ROOT/'src/config_files.h').read_text())
    # Use real implementation with minimal hardware/transport headers.
    for name in ['config_files.cpp', 'config_transfer.cpp']:
        (work/name).write_text((ROOT/'src'/name).read_text())
    (work/'main.cpp').write_text(MAIN)
    subprocess.run(['c++', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-fsanitize=address,undefined',
                    '-I'+str(work), '-I'+str(JSON), str(work/'config_files.cpp'), str(work/'config_transfer.cpp'),
                    str(work/'main.cpp'), '-o', str(work/'test')], check=True)
    subprocess.run([str(work/'test')], check=True)
print('PASS: backup/restore, project validation, writes/rename/space errors, staged upload, disconnect, parallel requests and loop commit.')
