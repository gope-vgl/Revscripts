#!/usr/bin/env bash
# save as curl_targets.sh and make executable: chmod +x curl_targets.sh
# Usage: ./curl_targets.sh ips.txt "http://example.com/path"   or
#        cat ips.txt | ./curl_targets.sh - "http://example.com/path"

set -euo pipefail
IFS=$'\n\t'

IP_FILE=${1:-}
URL=${2:-}

if [[ -z "$IP_FILE" || -z "$URL" ]]; then
  echo "Usage: $0 <ips_file|-> <url>"
  exit 2
fi

# read from file or stdin (-)
if [[ "$IP_FILE" == "-" ]]; then
  mapfile -t IPs
else
  mapfile -t IPs < "$IP_FILE"
fi

# options
CURL_OPTS=(--max-time 10 -sS -ku admin:cl4r0vtr)   # adjust timeout as you like
for line in "${IPs[@]}"; do
  # trim whitespace and ignore empty lines
  line=$(echo "$line" | tr -d '\r\n' | xargs)
  [[ -z "$line" || "$line" =~ ^# ]] && continue

  # extract hostname and ip (first and second columns)
  hostname=$(echo "$line" | awk '{print $1}')
  ip=$(echo "$line" | awk '{print $2}')

  # skip if either field is missing
  [[ -z "$hostname" || -z "$ip" ]] && continue

  # build target URL
  if [[ "$URL" =~ ^https?:// ]]; then
    scheme=${URL%%://*}
    rest=${URL#*://}
    path_part=""
    if [[ "$rest" == *"/"* ]]; then
      path_part="/${rest#*/}"
    fi
    target="${scheme}://${ip}${path_part}"
  else
    target="$URL"
  fi

  echo "---- Host: $hostname | IP: $ip | Target: $target ----"

  if output=$(curl "${CURL_OPTS[@]}" "$target" | jq 2>&1); then
    echo "$output" | sed "s/^/$hostname ($ip): /"
    echo "$hostname ($ip): curl OK"
  else
    echo "$hostname ($ip): curl FAILED"
    echo "$output" | sed "s/^/$hostname ($ip): /"
  fi
done
