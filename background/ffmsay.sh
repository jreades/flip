#!/usr/bin/env zsh

# Check for if the user wants to execute the command
flag_x=false
for arg in "$@"; do
    if [[ "$arg" == "-x" ]]; then
        flag_x=true
        break
    fi
done

# Hit the model and get the ffmpeg command
output=$(llm "$1" \
    --system "You are an expert at writing commands for ffmpeg. You will be given prompts describing what the user wants to do with ffmpeg. to the best of your abilities, translate these plain language descriptions into a single one-liner that calls ffmpeg, with all the appropriate flags and input/output specifications. Do not use the variable 'total_frames' in any select statement. Ensure the command is wrapped as a code block." \
    --extract)

# Print or execute the command
if [[ "$flag_x" == true ]]; then
    echo "$output"
    eval "$output"
else
    echo "$output"
fi