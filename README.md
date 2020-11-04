# Myriad Pre-Record Importer

This tool automatically imports audio files matching HCR's format specification to the Audiowall (under the 1500-1600 range), and generates the required logs to HCR's pre-recorded show clock format.

## Prerequisites

-   Python 3.6+
-   FFMpeg

## Usage
`python3 importer.py /path/to/audio/file/1.mp3 /path/to/audio/file/2.mp3 ... /path/to/audio/file/N.mp3`

| **Option**         | Description                                                  | Example                               |
| ------------------ | ------------------------------------------------------------ | ------------------------------------- |
| `--data-directory` | The path to the folder containing the Myriad data and 'Audiowall' folder.<br />Defaults to `C:\PSquared\` if unspecified. | `--data-directory C:\\PSquared\\`     |
| `--logs-directory` | The path to write the generated music logs to.<br />Defaults to `C:\PSquared\Logs` if unspecified. | `--logs-directory C:\\PSquared\\Logs` |

## Notes For Third Parties:

-   This tool will generate the requisite log files, but will *not* schedule them in playout. This is left to be done at the user's discretion.
-   This tool will remove the hour that the pre-recorded show is due to play out from the log, if it is already scheduled.
-   The format of the generated hour is hardcoded, but can be changed relatively easily using the `LogFileGenerator` set of functions.
-   The generated logs currently follow the default Myriad naming convention: `MY<YYMMDD>.LOG`.
-   The tool will convert the supplied audio files to WAV before importing to the Audiowall.

## Support

Please open a GitHub issue, or contact support@hcr923fm.com.