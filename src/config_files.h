#pragma once

#include <ArduinoJson.h>
#include <LittleFS.h>

// Shared by upload, backup and restore. Never remove a destination before rename.
namespace EspConfigFiles {
constexpr const char *active = "/config.json";
constexpr const char *backup = "/config_backup.json";
constexpr const char *temporary = "/config_backup.json.tmp";
// Unvalidated imports must not be picked up by legacy boot recovery.
constexpr const char *upload = "/config_import.json.tmp";
constexpr size_t reserve = 8192; // two LittleFS blocks for metadata/GC

bool hasSpace(size_t bytes);
bool valid(const char *path, const char *section);
const char *copy(const char *source, const char *destination, const char *section);
} // namespace EspConfigFiles
