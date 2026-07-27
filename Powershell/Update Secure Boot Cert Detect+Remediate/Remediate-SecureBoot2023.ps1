<#
Name: Remediate-SecureBoot2023.ps1
Author: Stephanie Fletcher-Davey

Description:
Forces a Windows machine to install the UEFI 2023 CA update from Microsoft.

Special thanks to this article: https://woshub.com/updating-uefi-secure-boot-certificates-windows-faq/ for being an excellent resource here. This script is based off the info in that guide.
#>
Start-Transcript -Path "C:\ProgramData\IntuneManagementExtension\Logs\Remediate-SecureBoot2023.log" -Append
# This registry setting tells Windows that it is allowed to install the new certificates
Set-ItemProperty -Path 'HKLM:\SYSTEM\CurrentControlSet\Control\SecureBoot' -Name 'AvailableUpdates' -Value 0x5944

# Run the Secure-Boot-Update scheduled task.
Start-ScheduledTask -TaskName '\Microsoft\Windows\PI\Secure-Boot-Update'

<#
When the user next restarts, the first part of the secure boot certificate install is run.
On their next boot, the above scheduled task is run again.
Upon the *next* power cycle, the secure boot certificate update will be completed.
If this remediation is triggered at any point during that process, it shouldn't affect anything.
The scheduled task is set up to run once every 12 hours in Windows by default.
All that will happen if this remediation runs again is the scheduled task will be run slightly more often.
#>
