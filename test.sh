#!/bin/bash

curl_path() {
  local pth="$1"
  local silent_flag="$2"
  local base_url="http://127.0.0.1:8000"
  local url
  local curl_options

  url="$base_url/$pth"

  if [[ -n "$silent_flag" ]]; then
    curl_options="-s -o /dev/null"
  fi

  curl ${curl_options} $url
  if [[ -z "$silent_flag" ]]; then
    echo
  fi
}

curl_queries() {
  curl_path "tpch/attached"
  curl_path "suppliers/top"
  curl_path "supplier/1/items/price/total"
}

# Create TPCH DuckDB files
curl_path "tpch/create" 1
# Attach V1 file
curl_path "tpch/attach/v1" 1
echo "V1 attached"
echo
# Run queries
curl_queries
echo
# Now attach V2
curl_path "tpch/attach/v2" 1
echo "V2 attached"
echo
# Queries should return different values
curl_queries
