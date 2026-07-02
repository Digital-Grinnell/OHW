# Function 1: Convert WAV, M4A, or MP4 to MP3

## Purpose
Convert WAV, M4A, or MP4 source files to standardized MP3 format for oral history recordings. Source files are preserved in their original format in the OHM output directory and converted directly to MP3.

## Requirements
- **ffmpeg** must be installed on your system
  - macOS: `brew install ffmpeg`
  - Linux: `sudo apt install ffmpeg`
  - Windows: Download from https://ffmpeg.org/download.html

## Usage

1. In the **Inputs** section, click **Browse...** to select a directory containing your audio files
2. Click **List WAV and MP3 Files** to scan the directory and all subdirectories
3. From the **Select Audio File** dropdown, choose the WAV, M4A, or MP4 file you want to convert
   - Files are displayed with relative paths (e.g., `subdir/file.wav`)
   - The app searches `~/OHM-data/` for an existing directory matching the file's basename
   - If found, it reuses that directory and epoch timestamp
   - If not found, it creates a new directory named `<sanitized-basename>--dg_<epoch>`
4. In the **Active Functions** dropdown, select **"🎵 1: Convert WAV/M4A/MP4 to MP3"**
5. The function will:
   - Open a **"Converting Audio to MP3"** progress dialog immediately — do not close the app or start other functions until it dismisses itself
   - **Step 1:** Copy the source audio to the output directory using its original extension, such as `dg_<epoch>.wav`, `dg_<epoch>.m4a`, or `dg_<epoch>.mp4`
   - **Step 2:** Convert that copied source file to `dg_<epoch>.mp3`
   - The dialog updates as each step completes, then closes automatically when done
6. Check the status bar and log output for the final result

> ⚠️ **Large files (1 GB+) can take several minutes to copy and convert.** The progress dialog will remain open throughout. Do not close the application until it dismisses.

## Output Directory

When you select a file for processing, OHM searches for an existing output directory in `~/OHM-data/` that matches the file's basename. If found, it reuses that directory and its epoch timestamp. If not found, it creates a new unique subdirectory with the naming pattern:

```
<sanitized-filename-without-extension>--dg_<unix-timestamp>
```

For example, selecting `interview_john_doe.wav` for the first time might create:
```
~/OHM-data/interview_john_doe--dg_1712345678/
```

If you select `interview_john_doe.wav` or `interview_john_doe.mp3` again later, the app will find and reuse the existing `interview_john_doe--dg_1712345678/` directory instead of creating a new one.

The converted files will use the directory's epoch timestamp:
```
~/OHM-data/interview_john_doe--dg_1712345678/dg_1712345678.wav (copied from source)
~/OHM-data/interview_john_doe--dg_1712345678/dg_1712345678.mp3 (converted)
```

If the source is M4A or MP4, the preserved source copy will be `dg_<epoch>.m4a` or `dg_<epoch>.mp4` instead of `dg_<epoch>.wav`.

All output files for this audio file will be stored in this directory. The source audio file is copied to the output directory with standardized naming before conversion. This keeps each oral history recording's outputs organized and allows you to work with the same file multiple times without creating duplicate directories.

## Technical Details

### Encoding Settings
- **Codec**: libmp3lame (LAME MP3 encoder)
- **Quality**: VBR (Variable Bit Rate) quality level 2
- **Average Bitrate**: ~190 kbps
- **Sample Rate**: 44100 Hz (44.1 kHz)

### File Handling
- When a file is selected, the app searches for an existing output directory matching the basename
- If found, that directory and its epoch are reused; if not, a new directory is created
- Source audio file is copied to the output directory under `~/OHM-data/` as `dg_<epoch>.wav`, `dg_<epoch>.m4a`, or `dg_<epoch>.mp4`
- Original source file remains unchanged in its original location
- If the copied source file already exists in the output directory, the copy step is skipped
- MP3 is created from the copied source audio file in the output directory as `dg_<epoch>.mp3`
- If `dg_<epoch>.mp3` already exists in the output directory, conversion is skipped
- Selecting the same file multiple times reuses the same output directory
- For M4A or MP4 sources, OHM does not create a WAV because transcoding lossy/compressed sources into WAV does not improve preservation quality; the original source file is the preservation copy

## Expected Results

A successful conversion will:
- Copy the source WAV, M4A, or MP4 to the output directory with its original extension (if not already present)
- Create an MP3 file named `dg_<epoch>.mp3` in the unique output directory under `~/OHM-data/`
- Display file sizes for the source audio and MP3 files
- Show compression ratio when the source is larger than the MP3, which is typical for WAV inputs
- Log the copy and conversion details with output location
- Keep the original source file unmodified in its original location

## Common Issues

### No file selected
**Problem**: Function executed without selecting a file
**Solution**: Use the Inputs section to select a directory and choose a file from the dropdown

### Unsupported source file
**Problem**: Selected file is an MP3 or other unsupported format
**Solution**: Function 1 currently accepts `.wav`, `.m4a`, and `.mp4` inputs. Select one of those formats.

### ffmpeg not found
**Problem**: The system cannot find the ffmpeg executable
**Solution**: Install ffmpeg using the appropriate method for your operating system

### Source file already copied
**Problem**: The preserved source file such as `dg_<epoch>.wav`, `dg_<epoch>.m4a`, or `dg_<epoch>.mp4` already exists in the output directory
**Result**: Copy step is skipped; conversion proceeds using the existing copied source file
**Note**: This is expected behavior and not an error

### Output file already exists
**Problem**: An MP3 file named `dg_<epoch>.mp3` already exists in the output directory
**Solution**: 
- This is expected if you've already converted this file - the app will skip the conversion
- To reconvert, manually delete the existing WAV/MP3 files in the output directory
- Note: Selecting the same file again will reuse the same output directory

### Conversion timeout
**Problem**: Conversion takes longer than 10 minutes
**Solution**: Check that the source file is not corrupted and that system resources are available

## Notes
- Large audio files may take time to copy and several minutes to convert
- The conversion is CPU-intensive; other applications may slow down temporarily
- Converted files are suitable for Digital.Grinnell oral history ingestion workflows
- The selected directory is remembered between sessions
- Output directories are reused when selecting files with the same basename
- This allows you to work with the same oral history file across multiple sessions
- All processing outputs for a single audio file are kept together in its output directory
- The source file is preserved in both its original location and copied to the output directory
- For M4A and MP4 sources, preserving the original source file is preferable to creating a synthetic WAV for archival storage
- If the copied source file and MP3 already exist in output directory, both copy and conversion steps are skipped
