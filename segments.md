# Audio Cuts

The format for this is fairly important and all four columns are required. The sequence does *not* need to be sequential, it is 'simply' used to generate an integer id that will be matched to a PNG file with the same number. Names are unimportant and solely to make it easier to know what is in the M4A file. As well, the start and end times can be any value matching the pattern `hh:mm:ss.ms` and gaps between end and start are allowed. Indeed, I do not recommend having the end time of one segment *exactly* match the start time of the next segment since it can lead to judder because of the way the audio is extracted. 

## Python the Basics-1

| Start    | End      | Sequence | Name               |
| -------- | -------- | -------- | ------------------ |
| 0:00.00  | 0:41.11  | 1        | Introduction       |
| 0:41.11  | 1:23.07  | 2        | Variables          |
| 1:23.07  | 3:41.05  | 3        | Types              |
| 3:41.05  | 5:49.08  | 6        | Change That        |
| 5:49.08  | 6:50.22  | 9        | All Objects        |

## Lists

| Start    | End      | Sequence | Name                 |
| -------- | -------- | -------- | -------------------- |
| 0:00.00  | 0:27.92  | 1        | Introduction         |
| 0:27.92  | 1:04.11  | 2        | What is a List 1     |
| 1:04.11  | 1:27.63  | 3        | What is a List 2     |
| 11:33.80 | 12:01.68 | 27       | Special List         |

## Mapping

| Start    | End      | Sequence | Name                      |
| -------- | -------- | -------- | ------------------------- |
| 0:00.00  | 0:38.07  | 1        | Introduction              |
| 0:38.08  | 3:04.28  | 2        | Two Cultures              |
| 3:04.29  | 3:57.04  | 3        | The Challenge             |
| -        | -        | 19       | Sheffield.mp4             |
