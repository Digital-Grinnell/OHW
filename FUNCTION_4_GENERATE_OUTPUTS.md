# Function 4: Generate TXT, VTT, CSV & PDF from JSON

## Purpose
Generate final output files (TXT, VTT, CSV, and PDF) from the edited JSON transcript created by Function 2. This allows you to perfect the transcript—fixing speaker names, correcting transcription errors, and adjusting content—before creating the final deliverable files.

## Requirements
- **Preferred workflow**: Function 2 creates the initial JSON transcript
- **Fallback workflow**: If the JSON is missing or contains no transcript segments, but a timestamped transcription DOCX is already present in the same output directory, Function 4 can now rebuild the JSON automatically and continue.
- **Edited content**: You can still edit the JSON to fix speaker names, spelling, etc. before re-running Function 4.

## Usage

1. **Preferred**: Run Function 2 to create the initial JSON transcript.
2. **Alternative**: If you already have a timestamped DOCX transcript in the output directory, skip Function 2 and let Function 4 rebuild the missing or empty JSON automatically.
3. **Edit the JSON file** located in `~/OHM-data/<sanitized-basename>--dg_<epoch>/dg_<epoch>_transcript.json`:
   - Change speaker labels (e.g., `"speaker": "SPEAKER_00"` → `"speaker": "John Doe"`)
   - Fix transcription errors in the `"text"` fields
   - Correct spelling and punctuation
   - Adjust timestamps if necessary
4. **Save the edited JSON** (maintain proper JSON format)
5. In the **Active Functions** dropdown, select **"📄 4: Generate TXT, VTT, CSV & PDF from JSON"**
6. The function will:
   - Read your edited JSON file
  - Or, if the JSON is missing or empty, locate a DOCX transcript in the same directory and build the JSON first
   - Generate a formatted TXT file with speaker labels
   - Generate a VTT subtitle file with speaker tags
   - Generate a CSV file with timestamp, speaker, and words columns
   - Generate a formatted PDF with timestamps and speaker labels
7. Monitor the status and log output for progress

## Output Directory

Files are generated in the same output directory as other processing:

```
~/OHM-data/<sanitized-basename>--dg_<epoch>/
```

For example:
```
~/OHM-data/interview_john_doe--dg_1712345678/
  ├── dg_1712345678.wav or .m4a          (preserved source copy from Function 1)
  ├── dg_1712345678.mp3                  (from Function 1)
  ├── dg_1712345678_transcript.json      (from Function 2, YOU EDIT THIS)
  ├── dg_1712345678.txt                  (from Function 4)
  ├── dg_1712345678.vtt                  (from Function 4)
  ├── dg_1712345678.csv                  (from Function 4)
  └── dg_1712345678.pdf                  (from Function 4)
```

## Output Files

Function 4 generates **4 final output files** from your edited JSON:

### 1. Plain Text (.txt)
- **Filename**: `dg_<epoch>.txt`
- **Contents**: Formatted transcript with timestamps and speaker labels
- **Format**:
  ```
  Audio file
  dg_1775499960.mp3

  Transcript

  [00:00:00] John Doe
  Hello, welcome to the interview.

  [00:00:05] Jane Smith
  Thank you for having me.
  ```
- **Use case**: Easy reading, printing, sharing, archival

### 2. WebVTT (.vtt)
- **Filename**: `dg_<epoch>.vtt`
- **Contents**: Web Video Text Tracks format with timestamps and speaker tags
- **Format**:
  ```
  WEBVTT

  00:00:00.000 --> 00:00:05.420
  <v John Doe>Hello, welcome to the interview.</v>

  00:00:05.420 --> 00:00:08.920
  <v Jane Smith>Thank you for having me.</v>
  ```
- **Use case**: HTML5 video subtitles, web accessibility, video editing

### 3. CSV (.csv)
- **Filename**: `dg_<epoch>.csv`
- **Contents**: Transcript data in spreadsheet-friendly format
- **Format**:
  ```
  timestamp,speaker,words
  00:00:00,John Doe,Hello welcome to the interview.
  00:00:05,Jane Smith,Thank you for having me.
  ```
- **Use case**: Data analysis, import into spreadsheets, database ingestion, further processing

### 4. PDF (.pdf)
- **Filename**: `dg_<epoch>.pdf`
- **Contents**: Formatted transcript with timestamps and speaker labels
- **Features**:
  - Descriptive document title: "Oral History Transcript: \<speaker names\>"
  - **Provenance section**: human-readable narrative from `notes.narrative`
  - Audio file header with MP3 filename
  - Transcript section with timestamps in [HH:MM:SS] format
  - Speaker names on the same line as timestamp
  - PDF metadata (title, author) for proper cataloguing

## JSON Structure

Here's what the JSON structure looks like (simplified):

```json
{
  "notes": {
    "narrative": "Human-readable provenance paragraph …",
    "created_at": "2026-04-07 14:24:13",
    "transcription_method": "MS Word Online (manual transcription)",
    "app": "OHM — Oral History Manager",
    "speaker_mapping": {
      "Interviewer": "Interviewer",
      "Speaker 1": "Jane Smith",
      "Reviewed By": "Mark McFate"
    },
    "source_audio": { "…": "technical metadata" }
  },
  "language": "en",
  "segments": [
    {
      "start": 0.0,
      "end": 5.42,
      "text": " Hello, welcome to the interview.",
      "speaker": "Interviewer"
    },
    {
      "start": 5.42,
      "end": 8.92,
      "text": " Thank you for having me.",
      "speaker": "Speaker 1"
    }
  ]
}
```

**Fields you can edit:**
- `speaker`: Change from SPEAKER_XX to real names, or enter `Interviewer` / `Speaker 1` etc.
- `text`: Fix transcription errors, spelling, punctuation
- `start`/`end`: Adjust timestamps (in seconds)

**Note:** The `notes` block is written by Function 2 and read by Function 4 to generate the PDF title and provenance section. Do not remove it.

## Technical Details

### Processing Workflow
1. Reads the JSON file from the output directory
2. Validates JSON structure
3. Generates TXT file with speaker labels and line breaks
4. Generates VTT file with timestamps and speaker voice tags
5. Generates CSV file with timestamp, speaker, and words columns
6. Generates PDF file with formatted transcript
7. All files reflect your edits from the JSON

### Speaker Label Formatting
- **TXT**: Speaker names appear on their own line followed by colon (`John Doe:`)
- **VTT**: Speaker names use voice tags (`<v John Doe>text</v>`)
- Speaker changes trigger new paragraphs/segments

### File Handling
- Overwrites existing TXT, VTT, CSV, and PDF files (allows regeneration after JSON edits)
- JSON file is read-only (never modified by this function)
- You can run Function 4 multiple times after editing JSON

## Common Issues

### "Transcript JSON not found"
- Function 4 now tries to rebuild the JSON from a DOCX transcript in the same output directory.
- If that still fails, make sure the DOCX file is present and timestamped in Word's transcript format.
- Make sure you're using the same file selection/output directory.
- If there is no DOCX file, run Function 2 first to create the initial JSON.

### "No segments found in JSON"
- Function 4 now treats this as a rebuild case and will try the DOCX transcript again.
- This commonly happens when an earlier DOCX conversion created an empty JSON because the transcript used a different heading format.

### "No segments found in JSON"
- JSON file may be corrupted or empty
- Re-run Function 2 to regenerate
- Check JSON syntax with a validator

### "Invalid JSON format"
- JSON editing introduced syntax errors
- Common issues: missing commas, unmatched brackets/quotes
- Use a JSON validator or editor with syntax highlighting
- Consider reverting to backup and re-editing

### Speaker names not appearing correctly
- Check that you edited the `"speaker"` field values
- Ensure speaker names are in quotes
- Names are case-sensitive
- Special characters in names should be properly escaped

## Tips for Editing JSON

1. **Use a proper editor**:
   - VS Code (built-in JSON support)
   - Any text editor with JSON syntax highlighting
   - Online JSON editors (with validation)

2. **Make a backup**:
   - Copy JSON file before editing
   - Keep original in case of mistakes

3. **Validate syntax**:
   - Many editors show errors in real-time
   - Use online JSON validators if unsure

4. **Common edits**:
   - Find/Replace all instances of "SPEAKER_00" with your speaker name
   - Use consistent naming for each speaker
   - Fix obvious transcription errors
   - Remove filler words if desired

5. **Test iteratively**:
   - Make small edits
   - Run Function 3 to generate outputs
   - Review results
   - Edit JSON again if needed
   - Re-run Function 3 (it's fast!)

## Workflow Summary

```
Preferred:
Function 2: Audio → JSON transcript (with provenance notes)
  ↓
[YOU EDIT JSON]
  ↓
Function 4: JSON → TXT + VTT + CSV + PDF (final outputs)

Fallback:
Existing DOCX transcript in output directory → Function 4 rebuilds JSON
  ↓
[OPTIONAL: YOU EDIT JSON]
  ↓
Function 4: JSON → TXT + VTT + CSV + PDF (final outputs)
```

This workflow gives you complete control over the final transcript while preserving all the benefits of automated transcription and speaker identification.
