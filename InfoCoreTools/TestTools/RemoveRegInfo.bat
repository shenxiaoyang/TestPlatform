echo off

reg delete "HKLM\SYSTEM\CurrentControlSet\Services\OSNService\Parameters" /v Arbiter /f
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\OSNService\Parameters" /v Roler /f
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\OSNService\Parameters" /v GroupId /f
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\OSNService\Parameters" /v LocalId /f
reg delete "HKLM\SYSTEM\CurrentControlSet\Services\OSNService\Parameters" /v NewFlag /f