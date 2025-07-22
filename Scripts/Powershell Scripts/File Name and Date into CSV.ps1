$folders = Get-ChildItem -Directory | Select-Object Name, @{Name="CreationDate";Expression={$_.CreationTime}}
$folders | Export-Csv -Path ".\FileNameAndDate.csv" -NoTypeInformation
