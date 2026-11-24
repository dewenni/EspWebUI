#include "EspWebUI.h"
#include "config_files.h"
#include <cstdlib>
#include <ctime>

namespace {
// POD, owned by AsyncWebServerRequest::_tempObject (freed by the request).
struct ConfigUpload {
  bool ownsFile;
  bool staged;
  bool final;
  size_t bytes;
  const char *error;
};

void fileTime(const char *path, char (&text)[32]) {
  text[0] = '\0';
  File file = LittleFS.open(path, FILE_READ);
  if (!file) return;
  const time_t stamp = file.getLastWrite();
  file.close();
  // Files written before time synchronization have no trustworthy date.
  if (stamp < 1704067200) return;
  tm local;
  if (localtime_r(&stamp, &local)) strftime(text, sizeof(text), "%Y-%m-%d %H:%M:%S", &local);
}
} // namespace

void EspWebUI::sendConfigFileStatus(const char *result, const char *area) {
  JsonDocument doc;
  doc["type"] = "configFiles";
  char saved[32], copied[32];
  fileTime(EspConfigFiles::active, saved);
  fileTime(EspConfigFiles::backup, copied);
  doc["savedAt"] = saved;
  doc["backupAt"] = copied;
  doc["backupExists"] = LittleFS.exists(EspConfigFiles::backup);
  if (result) doc["result"] = result;
  if (area) doc["area"] = area;
  sendWs(doc);
}

bool EspWebUI::handleConfigFileCommand(const char *elementID, const char *value) {
  if (strcmp(elementID, "config_files") != 0) return false;
  if (strcmp(value, "status") == 0) {
    sendConfigFileStatus();
    return true;
  }
  const bool restore = strcmp(value, "restore") == 0;
  if (!restore && strcmp(value, "backup") != 0) return true;
  bool expected = false;
  if ((callbackConfigFileReady && !callbackConfigFileReady()) ||
      !configFileBusy.compare_exchange_strong(expected, true)) {
    sendConfigFileStatus("config_files_busy", "backup");
    return true;
  }
  const char *error = EspConfigFiles::copy(restore ? EspConfigFiles::backup : EspConfigFiles::active,
                                         restore ? EspConfigFiles::active : EspConfigFiles::backup, configFileSection);
  sendConfigFileStatus(error ? error : restore ? "config_files_restored" : "config_files_created", "backup");
  if (!error && restore && callbackUpload) callbackUpload(UPLOAD_FINISH, "config_files_restored");
  configFileBusy = false;
  return true;
}

void EspWebUI::processConfigUpload() {
  // AsyncTCP stages a file; only the application loop may commit/restart.
  if (!configUploadPending.exchange(false)) return;
  const char *error = nullptr;
  if (callbackConfigFileReady && !callbackConfigFileReady()) error = "config_files_busy";
  else if (!EspConfigFiles::valid(EspConfigFiles::upload, configFileSection)) error = "config_files_invalid";
  else if (!LittleFS.rename(EspConfigFiles::upload, EspConfigFiles::active)) error = "config_files_failed";
  if (error) LittleFS.remove(EspConfigFiles::upload);
  sendConfigFileStatus(error ? error : "config_files_imported", "import");
  if (!error && callbackUpload) callbackUpload(UPLOAD_FINISH, "config_files_imported");
  configFileBusy = false;
}

void EspWebUI::setupConfigUploadRoute() {
  server.on("/config-backup-download", HTTP_GET, [this](AsyncWebServerRequest *request) {
    if (!isAuthenticated(request)) {
      request->send(401, "application/json", "{\"error\":\"not_authenticated\"}");
      return;
    }
    if (!LittleFS.exists(EspConfigFiles::backup)) {
      request->send(404, "application/json", "{\"error\":\"config_files_missing\"}");
      return;
    }
    auto *response = request->beginResponse(LittleFS, EspConfigFiles::backup, "application/json", true);
    response->addHeader("Cache-Control", "no-store");
    request->send(response);
  });

  server.on("/config-upload", HTTP_POST,
    [this](AsyncWebServerRequest *request) {
      if (!isAuthenticated(request)) {
        request->send(401, "application/json", "{\"error\":\"config_files_connection\"}");
        return;
      }
      auto *ctx = static_cast<ConfigUpload *>(request->_tempObject);
      if (!ctx || ctx->error || !ctx->final) {
        const char *error = ctx && ctx->error ? ctx->error : "config_files_failed";
        if (ctx && ctx->ownsFile) {
          request->_tempFile.close();
          LittleFS.remove(EspConfigFiles::upload);
          ctx->ownsFile = false;
          configFileBusy = false;
        }
        JsonDocument doc;
        doc["error"] = error;
        String body;
        serializeJson(doc, body);
        request->send(400, "application/json", body);
        return;
      }
      ctx->staged = true;
      configUploadPending = true;
      request->send(202, "application/json", "{\"accepted\":true}");
    },
    [this](AsyncWebServerRequest *request, const String &, size_t index, uint8_t *data, size_t len, bool final) {
      if (!isAuthenticated(request)) return;
      auto *ctx = static_cast<ConfigUpload *>(request->_tempObject);
      if (!ctx) {
        ctx = static_cast<ConfigUpload *>(calloc(1, sizeof(ConfigUpload)));
        if (!ctx) return;
        request->_tempObject = ctx;
        bool expected = false;
        ctx->ownsFile = configFileBusy.compare_exchange_strong(expected, true);
        if (!ctx->ownsFile) ctx->error = "config_files_busy";
        // A disconnected/incomplete upload never replaces either saved file.
        request->onDisconnect([this, request, ctx]() {
          if (ctx->ownsFile && !ctx->staged) {
            request->_tempFile.close();
            LittleFS.remove(EspConfigFiles::upload);
            configFileBusy = false;
          }
        });
        if (!ctx->error && !EspConfigFiles::hasSpace(request->contentLength())) ctx->error = "config_files_space";
        if (!ctx->error) {
          request->_tempFile = LittleFS.open(EspConfigFiles::upload, FILE_WRITE);
          if (!request->_tempFile) ctx->error = "config_files_failed";
        }
      }
      if (ctx->error) return;
      if (callbackConfigFileReady && !callbackConfigFileReady()) { ctx->error = "config_files_busy"; return; }
      // Reject multiple files and missing/reordered chunks in the same request.
      if (ctx->final || index != ctx->bytes) { ctx->error = "config_files_failed"; return; }
      if (len && request->_tempFile.write(data, len) != len) { ctx->error = "config_files_failed"; return; }
      ctx->bytes += len;
      if (final) {
        request->_tempFile.flush();
        request->_tempFile.close();
        File check = LittleFS.open(EspConfigFiles::upload, FILE_READ);
        if (!check || check.size() != ctx->bytes || ctx->bytes == 0) ctx->error = "config_files_failed";
        check.close();
        ctx->final = true;
      }
    });
}
