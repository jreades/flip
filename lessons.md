# Audio Cuts

The format for this is fairly important and all four columns are required. The sequence does *not* need to be sequential, it is 'simply' used to generate an integer id that will be matched to a PNG file with the same number. Names are unimportant and solely to make it easier to know what is in the M4A file. As well, the start and end times can be any value matching the pattern `hh:mm:ss.ms` and gaps between end and start are allowed. Indeed, I do not recommend having the end time of one segment *exactly* match the start time of the next segment since it can lead to judder because of the way the audio is extracted. 

## Python the Basics-1

| Start    | End      | Sequence | Name               |
| -------- | -------- | -------- | ------------------ |
| 0:00.00  | 0:41.11  | 1        | Introduction       |
| 0:41.11  | 1:23.07  | 2        | Variables          |
| 1:23.08  | 3:41.05  | 3        | Types              |

## Iteration

| Start    | End      | Sequence | Name            |
| -------- | -------- | -------- | --------------- |
| 0:01.23  | 0:33.62  | 1        | Introduction    |
| 0:34.19  | 01:00.62 | 2        | Definition      |
| 01:01.10 | 01:34.10 | 3        | Two Types       |

## Mapping

| Start    | End      | Sequence | Name                      |
| -------- | -------- | -------- | ------------------------- |
| 0:00.00  | 0:38.07  | 1        | Introduction              |
| 0:38.08  | 3:04.28  | 2        | Two Cultures              |
| 3:04.29  | 3:57.04  | 3        | The Challenge             |
| -        | -        | 19       | Sheffield.mp4             |
