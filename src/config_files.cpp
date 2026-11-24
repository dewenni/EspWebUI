#include "config_files.h"

namespace EspConfigFiles {
bool hasSpace(size_t bytes) {
  const size_t total = LittleFS.totalBytes(), used = LittleFS.usedBytes();
  return total >= used && total - used >= reserve && bytes <= total - used - reserve;
}

bool valid(const char *path, const char *section) {
  File file = LittleFS.open(path, FILE_READ);
  if (!file) return false;
  JsonDocument document;
  const auto error = deserializeJson(document, file);
  bool result = !error && document.is<JsonObject>() &&
                (!section || !section[0] || document[section].is<JsonObject>());
  // ArduinoJson stops after the root object: reject trailing non-whitespace.
  while (result && file.available()) {
    const int c = file.read();
    result = c == ' ' || c == '\r' || c == '\n' || c == '\t';
  }
  file.close();
  return result;
}

const char *copy(const char *source, const char *destination, const char *section) {
  if (!valid(source, section)) return "config_files_invalid";
  File input = LittleFS.open(source, FILE_READ);
  if (!input) return "config_files_failed";
  const size_t expected = input.size();
  if (!hasSpace(expected)) {
    input.close();
    return "config_files_space";
  }
  File output = LittleFS.open(temporary, FILE_WRITE);
  if (!output) {
    input.close();
    return "config_files_failed";
  }
  uint8_t buffer[256];
  size_t copied = 0;
  while (copied < expected) {
    const size_t wanted = expected - copied < sizeof(buffer) ? expected - copied : sizeof(buffer);
    const size_t received = input.read(buffer, wanted);
    if (received != wanted || output.write(buffer, received) != received) break;
    copied += received;
  }
  output.flush();
  output.close();
  input.close();
  File check = LittleFS.open(temporary, FILE_READ);
  bool complete = check && check.size() == expected && copied == expected;
  check.close();
  if (!complete || !valid(temporary, section)) {
    LittleFS.remove(temporary);
    return "config_files_failed";
  }
  // LittleFS atomically replaces an existing file. Keep both files on failure.
  if (!LittleFS.rename(temporary, destination)) return "config_files_failed";
  return nullptr;
}
} // namespace EspConfigFiles
