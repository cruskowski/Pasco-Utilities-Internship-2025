
param(
    [Parameter(Mandatory=$true)]
    [string]$SearchPath,
    
    [Parameter(Mandatory=$true)]
    [string]$CsvFilePath,
    
    [Parameter(Mandatory=$false)]
    [string]$OutputPath = ".\zipped folders"
)

# Function to create directory if it doesn't exist
function New-Directory {
    param([string]$Path)
    if (-not (Test-Path $Path)) {
        New-Item -ItemType Directory -Path $Path -Force | Out-Null
        Write-Host "Created directory: $Path" -ForegroundColor Green
    }
}

# Function to sanitize filename for Windows
function Get-SafeFileName {
    param([string]$Name)
    $invalidChars = [IO.Path]::GetInvalidFileNameChars()
    $safeName = $Name
    foreach ($char in $invalidChars) {
        $safeName = $safeName.Replace($char, '_')
    }
    return $safeName
}

# Main script execution
try {
    Write-Host "Starting folder search and zip process..." -ForegroundColor Cyan
    
    # Validate input parameters
    if (-not (Test-Path $SearchPath)) {
        throw "Search path does not exist: $SearchPath"
    }
    
    if (-not (Test-Path $CsvFilePath)) {
        throw "CSV file does not exist: $CsvFilePath"
    }
    
    # Create output directory
    New-Directory -Path $OutputPath
    
    # Create an array to track failures
    $failedZips = @()
    
    # Read CSV file
    Write-Host "Reading CSV file: $CsvFilePath" -ForegroundColor Yellow
    $csvData = Import-Csv $CsvFilePath
    
    # Check if CSV has the expected structure
    if (-not $csvData) {
        throw "CSV file is empty or could not be read"
    }
    
    # Get the first property name from CSV (assuming it contains the title parts)
    $firstRow = $csvData | Select-Object -First 1
    if (-not $firstRow) {
        throw "CSV file does not contain any data rows."
    }
    $titleProperty = ($firstRow | Get-Member -MemberType NoteProperty | Select-Object -First 1).Name
    if (-not $titleProperty) {
        throw "CSV file does not contain any columns."
    }
    Write-Host "Using column '$titleProperty' for title parts" -ForegroundColor Yellow
    
    # Process each title part from CSV
    foreach ($row in $csvData) {
        $titlePart = $row.$titleProperty
        
        if ([string]::IsNullOrWhiteSpace($titlePart) -or $titlePart -eq "PCU_NUM") {
            Write-Host "Skipping empty or header row: '$titlePart'" -ForegroundColor Yellow
            continue
        }
        
        Write-Host "`nProcessing PCU number: '$titlePart'" -ForegroundColor Cyan
        
        # Search for folders containing the PCU number (using wildcard search)
        $matchingFolders = Get-ChildItem -Path $SearchPath -Directory | 
                          Where-Object { $_.Name -like "*$titlePart*" }
        
        if ($matchingFolders.Count -eq 0) {
            Write-Host "No folders found containing PCU number '$titlePart'" -ForegroundColor Red
            # Add to failed zips array with details
            $failedZips += [PSCustomObject]@{
                PCU_Number = $titlePart
                Folder = "No matching folders found"
                SubFolder = "N/A"
                Error = "No folders matching PCU number"
            }
            continue
        }
        
        # Process each matching folder
        foreach ($folder in $matchingFolders) {
            Write-Host "Found matching folder: $($folder.FullName)" -ForegroundColor Green
            
            # Look for subfolder
            $eorFolder = Get-ChildItem -Path $folder.FullName -Directory | 
                        Where-Object { $_.Name -eq "EOR Submittals-Responses" -or $_.Name -eq "Submittals and Responses" }
            
            if ($eorFolder) {
                Write-Host "Found $($eorFolder.Name) folder in: $($folder.Name)" -ForegroundColor Green
                
                # Create safe filename for zip
                $safeTitle = Get-SafeFileName -Name $titlePart
                $zipFileName = "$safeTitle.zip"
                $zipPath = Join-Path $OutputPath $zipFileName
                
                # Remove existing zip if it exists
                if (Test-Path $zipPath) {
                    Remove-Item $zipPath -Force
                    Write-Host "Removed existing zip file: $zipFileName" -ForegroundColor Yellow
                }
                
                try {
                    # Create zip file using 7-Zip for best long path support
                    Write-Host "Creating zip file: $zipFileName" -ForegroundColor Yellow
                    
                    # Check if 7-Zip is available
                    $sevenZipPath = "C:\Program Files\7-Zip\7z.exe"
                    if (-not (Test-Path $sevenZipPath)) {
                        $sevenZipPath = "C:\Program Files (x86)\7-Zip\7z.exe"
                    }
                    
                    if (Test-Path $sevenZipPath) {
                        # Use 7-Zip (best for handling very long paths)
                        Write-Host "Using 7-Zip for better long path support" -ForegroundColor Yellow
                        
                        # Create zip with 7-Zip
                        $sevenZipArgs = "a -tzip `"$zipPath`" `"$($eorFolder.FullName)\*`" -r -mx=5"
                        $sevenZipProcess = Start-Process -FilePath $sevenZipPath -ArgumentList $sevenZipArgs -NoNewWindow -PassThru -Wait
                        
                        if ($sevenZipProcess.ExitCode -ne 0) {
                            throw "7-Zip failed with exit code: $($sevenZipProcess.ExitCode)"
                        }
                    }
                    else {
                        # 7-Zip not found, try alternative approach with robocopy
                        Write-Host "7-Zip not found, using alternate method" -ForegroundColor Yellow
                        
                        # Use alternate method with shorter paths
                        $tempDir = Join-Path $env:TEMP "PCUTempCopy_$(Get-Random)"
                        New-Item -Path $tempDir -ItemType Directory -Force | Out-Null
                        
                        Write-Host "Using temporary directory: $tempDir" -ForegroundColor Yellow
                        
                        # Copy files to temp location with robocopy (handles long paths better)
                        $robocopyResult = Start-Process -FilePath "robocopy.exe" -ArgumentList "`"$($eorFolder.FullName)`" `"$tempDir`" /E /MT:4 /R:1 /W:1 /NJH /NJS" -NoNewWindow -PassThru -Wait
                        
                        if ($robocopyResult.ExitCode -lt 8) {
                            # Add .NET ZipFile class
                            Add-Type -AssemblyName System.IO.Compression.FileSystem
                            
                            try {
                                # Create zip from temp location using PowerShell command
                                Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force
                            }
                            catch {
                                # If PowerShell command fails, try native .NET method
                                try {
                                    [System.IO.Compression.ZipFile]::CreateFromDirectory($tempDir, "$zipPath.temp", [System.IO.Compression.CompressionLevel]::Optimal, $false)
                                    
                                    # If successful, rename the temp file
                                    if (Test-Path "$zipPath.temp") {
                                        Move-Item -Path "$zipPath.temp" -Destination $zipPath -Force
                                    } else {
                                        throw "Zip file not created"
                                    }
                                }
                                catch {
                                    # Last resort - try the shell COM object
                                    Write-Host "Trying Shell.Application method..." -ForegroundColor Yellow
                                    $shellApp = New-Object -ComObject Shell.Application
                                    $zipFile = $shellApp.NameSpace($zipPath)
                                    if ($zipFile -ne $null) {
                                        $zipFile.CopyHere($tempDir)
                                        # Wait for the zip operation to complete
                                        Start-Sleep -Seconds 5
                                    } else {
                                        throw "Failed to create zip using Shell.Application"
                                    }
                                }
                            }
                            
                            # Clean up temp directory
                            Remove-Item -Path $tempDir -Recurse -Force -ErrorAction SilentlyContinue
                        } else {
                            throw "Failed to copy files with robocopy. Exit code: $($robocopyResult.ExitCode)"
                        }
                    }
                    
                    # Verify the zip was created
                    if (Test-Path $zipPath) {
                        Write-Host "Successfully created: $zipPath" -ForegroundColor Green
                        
                        # Break after first successful match to avoid duplicates
                        break
                    } else {
                        throw "Zip file was not created at expected location: $zipPath"
                    }
                }
                catch {
                    Write-Host "Error creating zip file for '$titlePart': $($_.Exception.Message)" -ForegroundColor Red
                    # Add to failed zips array with details
                    $failedZips += [PSCustomObject]@{
                        PCU_Number = $titlePart
                        Folder = $folder.FullName
                        SubFolder = $eorFolder.Name
                        Error = $_.Exception.Message
                    }
                }
            }
            else {
                Write-Host "No 'EOR Submittals-Responses' or 'Submittals and Responses' folder found in: $($folder.Name)" -ForegroundColor Yellow
                # Add to failed zips array with details
                $failedZips += [PSCustomObject]@{
                    PCU_Number = $titlePart
                    Folder = $folder.FullName
                    SubFolder = "Missing"
                    Error = "Required subfolder not found"
                }
            }
        }
    }
    
    # Export failed zip data if any failures occurred
    if ($failedZips.Count -gt 0) {
        $failureCsvPath = Join-Path $OutputPath "failed_zips_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
        $failedZips | Export-Csv -Path $failureCsvPath -NoTypeInformation
        Write-Host "`nWarning: $($failedZips.Count) PCU numbers failed to zip." -ForegroundColor Yellow
        Write-Host "Details saved to: $failureCsvPath" -ForegroundColor Yellow
    } else {
        Write-Host "`nAll PCU numbers were processed successfully!" -ForegroundColor Green
    }
    
    Write-Host "`nProcess completed!" -ForegroundColor Green
    Write-Host "Zipped folders saved to: $OutputPath" -ForegroundColor Green
}
catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
    
    # Try to save any failures that occurred before the exception
    if ($failedZips -and $failedZips.Count -gt 0) {
        $failureCsvPath = Join-Path $OutputPath "failed_zips_error_$(Get-Date -Format 'yyyyMMdd_HHmmss').csv"
        $failedZips | Export-Csv -Path $failureCsvPath -NoTypeInformation
        Write-Host "Partial failure list saved to: $failureCsvPath" -ForegroundColor Yellow
    }
    
    exit 1
}
