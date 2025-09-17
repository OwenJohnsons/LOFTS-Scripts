#!/bin/bash
# filterbank-gen-lofts.sh

# ===== CLI =====
DRY_RUN=false
SKIP_TARGETS=()

usage() {
    cat <<EOF
Usage: $0 [-dry|--dry-run] [--skip|--skip-target <name[,name2,...]>] <directory_path> <IE|SE>

Options:
  -dry, --dry-run          Print commands without executing.
      --skip LIST          Comma-separated list of targets (or glob patterns) to skip.
      --skip-target LIST   Alias of --skip. Can be provided multiple times.

Matching behavior:
  - Matches either full scan ID (e.g., "01_B0329+54") or base name ("B0329+54").
  - Shell globs supported: "01_*", "B03*", etc.
EOF
    exit 1
}

# Parse flags
while [[ "$1" == -* ]]; do
  case "$1" in
    -dry|--dry-run)
      DRY_RUN=true; shift ;;
    --skip|--skip-target)
      [[ -z "$2" ]] && { echo "ERROR: $1 requires a value"; usage; }
      while IFS= read -r item; do
        item_trimmed="$(echo "$item" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        [[ -n "$item_trimmed" ]] && SKIP_TARGETS+=("$item_trimmed")
      done < <(printf "%s" "$2" | tr ',' '\n')
      shift 2 ;;
    -h|--help) usage ;;
    --) shift; break ;;
    *)
      echo "Unknown option: $1"
      usage ;;
  esac
done

# Args
path=$1       # e.g. /datax/Projects/.../sess_sidYYYYMMDDTHHMMSS_SE607[/scan_*]
station=$2    # IE or SE
[[ -z "$path" || -z "$station" ]] && usage

# ===== Helpers =====
run() { if $DRY_RUN; then echo "[DRY-RUN] $*"; else "$@"; fi; }

# match full scan id OR base name; support globs
should_skip_target() {
  local scan_id="$1"               # e.g., 01_B0329+54
  local base_name="${scan_id#*_}"  # -> B0329+54
  for pat in "${SKIP_TARGETS[@]}"; do
    [[ "$scan_id" == $pat || "$base_name" == $pat ]] && return 0
  done
  return 1
}

set +x 2>/dev/null

# ===== Station config =====
if [[ "$station" != "IE" && "$station" != "SE" ]]; then
    echo "Invalid station prefix. Use IE or SE. Exiting..."
    exit 1
fi

if [[ "$station" == "IE" ]]; then
    port_prefix=1613
    station_prefix="IE613_16130"
else
    port_prefix=1607
    station_prefix="SE607_16070"
fi
station_code=${station_prefix%%_*}   # e.g., SE607 or IE613

# ===== Logging setup =====
time_now=$(date +"%H:%M")
log_name=$(basename "$path")
log_dir="/datax2/projects/LOFTS/logs/filgen"
run mkdir -p "$log_dir"
log_file="${log_dir}/${log_name}_${time_now}.out"
error_file="${log_dir}/${log_name}_${time_now}.err"

{
echo "===== Script started at $(date) ====="
echo "Directory: $path"
echo "Station: $station"
$DRY_RUN && echo "Mode: DRY-RUN (side-effect commands will not execute)"
echo "Skip list: ${SKIP_TARGETS[*]:-(none)}"

# ===== Discover scan folders =====
# Accept either a parent session dir or a single scan_* dir
if [[ -d "$path" && "$(basename "$path")" =~ ^scan_ ]]; then
    folders="$path"
else
    folders=$(find "$path" -type d \( -name "scan_*" -o -name "*scan_B*" \))
fi

# Extract YYYY-MM-DD from 'sidYYYYMMDD' anywhere in the path; fallback to today if missing
sid_date=$(echo "$path" | sed -nE 's#.*sid([0-9]{8})T.*#\1#p' | head -n1)
if [[ -n "$sid_date" ]]; then
    date="${sid_date:0:4}-${sid_date:4:2}-${sid_date:6:2}"
else
    date=$(date +%F)
    echo "WARNING: Could not extract sidYYYYMMDD from path; using today: $date"
fi

echo "Number of folders found : $(echo "$folders" | wc -w)"
echo "Date of observations: $date"

for folder in $folders; do
    echo "-------------------------------"
    echo "Processing folder: $folder"

    target=$(basename "$folder" | sed 's/^.\{5\}//')
    echo "Processing Target : $target"

    if should_skip_target "$target"; then # this doesn't work at present 
        echo "Skipping target '$target' as requested."
        continue
    fi

    output_dir="/datax2/projects/LOFTS/$date/$target"
    if [[ ! -d "$output_dir" ]]; then
        echo "Creating output directory: $output_dir"
        run mkdir -p "$output_dir"
        run chmod o+r "$output_dir" 2>/dev/null || true
        run chown -R 1000:1000 "$output_dir"
    fi
    echo "Output directory: $output_dir"

    # ===== Skip extractor if .fil already present =====
    fil_files=$(find "$output_dir" -name "*.fil" 2>/dev/null)
    if [[ -n "$fil_files" ]]; then
        echo "Filterbank files already exist in $output_dir. Skipping lofar_udp_extractor..."
        fil_exist=true
    else
        fil_exist=false
<<<<<<< HEAD

        # ---- Locate log ----
        log_file_scan=$(find "$folder" -maxdepth 1 -type f -name "*.log" | head -n 1)

        # ---- Find BFS dir ----
        bfs_dir=$(find "$folder" -maxdepth 1 -type d -name "${station_code}_*_bfs" | head -n 1)

        # ---- Locate header ----
        metadata=""
        if [[ -n "$bfs_dir" && -d "$bfs_dir" ]]; then
            # 1) Prefer *_bfs.h (e.g., 20250726_090100_bfs.h)
            metadata=$(find "$bfs_dir" -maxdepth 1 -type f -name "*_bfs.h" | head -n 1)
            # 2) If not found, accept any .h in BFS dir
            [[ -z "$metadata" ]] && metadata=$(find "$bfs_dir" -maxdepth 1 -type f -name "*.h" | head -n 1)
        fi
        [[ -z "$metadata" ]] && metadata=$(find "$folder" -maxdepth 1 -type f -name "*.h" | head -n 1)

        if [[ -z "$metadata" ]]; then
            echo "FATAL: No header (.h) file found (looked in $bfs_dir and $folder). Cannot run extractor." >&2
            continue
        fi
        echo "Metadata header: $metadata"

        # ===== .zst path with [[port]] =====
        if [[ -n "$bfs_dir" && -d "$bfs_dir" ]]; then
            udp_example=$(find "$bfs_dir" -maxdepth 1 -type f -name "udp_${station_code}_${port_prefix}*.blc*.zst" | head -n 1)
            if [[ -z "$udp_example" ]]; then
                if [[ -n "$log_file_scan" ]]; then
                    zst_scan_path_raw=$(awk 'NR==4 {print $2}' "$log_file_scan")
                    zst_scan_path=$(echo "$zst_scan_path_raw" | sed -E "s/(udp_${station_code}_${port_prefix})([0-9]{1,2})/\1[[port]]/")
                    echo "WARNING: Using log-derived path (no UDP .zst files found in *_bfs)."
                else
                    echo "FATAL: No UDP .zst files in *_bfs and no .log fallback. Skipping folder."
                    continue
                fi
            else
                udp_basename=$(basename "$udp_example")
                udp_template=$(echo "$udp_basename" | sed -E "s/(udp_${station_code}_${port_prefix})([0-2]?[0-9])/\1[[port]]/")
                zst_scan_path="${bfs_dir}/${udp_template}"
                
            fi
        else
            if [[ -n "$log_file_scan" ]]; then
                zst_scan_path_raw=$(awk 'NR==4 {print $2}' "$log_file_scan")
                zst_scan_path=$(echo "$zst_scan_path_raw" | sed -E "s/(udp_${station_code}_${port_prefix})([0-9]{1,2})/\1[[port]]/")
                echo "WARNING: Using log-derived path (no *_bfs directory found)."
            else
                echo "FATAL: No *_bfs directory and no .log to derive .zst path. Skipping folder."
                continue
            fi
        fi

        echo "Scan path: $zst_scan_path"

        # --- Grabbing start time for skip --- 
        zst_start="${zst_scan_path: -27:19}"
        jump_time=$(date -d "$zst_start 20 seconds" +"%Y-%m-%dT%H:%M:%S")

=======

        # ---- Locate log ----
        log_file_scan=$(find "$folder" -maxdepth 1 -type f -name "*.log" | head -n 1)

        # ---- Find BFS dir ----
        bfs_dir=$(find "$folder" -maxdepth 1 -type d -name "${station_code}_*_bfs" | head -n 1)

        # ---- Locate header ----
        metadata=""
        if [[ -n "$bfs_dir" && -d "$bfs_dir" ]]; then
            # 1) Prefer *_bfs.h (e.g., 20250726_090100_bfs.h)
            metadata=$(find "$bfs_dir" -maxdepth 1 -type f -name "*_bfs.h" | head -n 1)
            # 2) If not found, accept any .h in BFS dir
            [[ -z "$metadata" ]] && metadata=$(find "$bfs_dir" -maxdepth 1 -type f -name "*.h" | head -n 1)
        fi
        [[ -z "$metadata" ]] && metadata=$(find "$folder" -maxdepth 1 -type f -name "*.h" | head -n 1)

        if [[ -z "$metadata" ]]; then
            echo "FATAL: No header (.h) file found (looked in $bfs_dir and $folder). Cannot run extractor." >&2
            continue
        fi
        echo "Metadata header: $metadata"

        # ===== .zst path with [[port]] =====
        if [[ -n "$bfs_dir" && -d "$bfs_dir" ]]; then
            udp_example=$(find "$bfs_dir" -maxdepth 1 -type f -name "udp_${station_code}_${port_prefix}*.blc*.zst" | head -n 1)
            if [[ -z "$udp_example" ]]; then
                if [[ -n "$log_file_scan" ]]; then
                    zst_scan_path_raw=$(awk 'NR==4 {print $2}' "$log_file_scan")
                    zst_scan_path=$(echo "$zst_scan_path_raw" | sed -E "s/(udp_${station_code}_${port_prefix})([0-9]{1,2})/\1[[port]]/")
                    echo "WARNING: Using log-derived path (no UDP .zst files found in *_bfs)."
                else
                    echo "FATAL: No UDP .zst files in *_bfs and no .log fallback. Skipping folder."
                    continue
                fi
            else
                udp_basename=$(basename "$udp_example")
                udp_template=$(echo "$udp_basename" | sed -E "s/(udp_${station_code}_${port_prefix})([0-2]?[0-9])/\1[[port]]/")
                zst_scan_path="${bfs_dir}/${udp_template}"
            fi
        else
            if [[ -n "$log_file_scan" ]]; then
                zst_scan_path_raw=$(awk 'NR==4 {print $2}' "$log_file_scan")
                zst_scan_path=$(echo "$zst_scan_path_raw" | sed -E "s/(udp_${station_code}_${port_prefix})([0-9]{1,2})/\1[[port]]/")
                echo "WARNING: Using log-derived path (no *_bfs directory found)."
            else
                echo "FATAL: No *_bfs directory and no .log to derive .zst path. Skipping folder."
                continue
            fi
        fi

        echo "Scan path: $zst_scan_path"

>>>>>>> bb3f917c3a2e43a45031ea73c5af0ef985e62d33
        # ---- Run UDP ----
        raw_files=$(find "$output_dir" -name "*.raw" 2>/dev/null)
        if [[ -n "$raw_files" ]]; then
            echo "Raw files already exist in $output_dir. Skipping lofar_udp_extractor..."
        else
            echo "Running lofar_udp_extractor..."
            run singularity exec --bind /datax,/datax2 /datax2/obs/singularity/lofar-upm_latest.simg \
<<<<<<< HEAD
                lofar_udp_extractor -p 30 -t "${jump_time}" -M GUPPI \
=======
                lofar_udp_extractor -p 30 -M GUPPI \
>>>>>>> bb3f917c3a2e43a45031ea73c5af0ef985e62d33
                -S 1 -b 0,412 \
                -i "${zst_scan_path}" \
                -o "${output_dir}/${target}.[[iter]].raw" \
                -m 4096 -I "${metadata}"
<<<<<<< HEAD
            
=======
            # Ensure ownership after extractor
>>>>>>> bb3f917c3a2e43a45031ea73c5af0ef985e62d33
            run chown -R 1000:1000 "$output_dir"
        fi
    fi

    # ===== rawspec =====
    if [[ -f "$output_dir/${target}.rawspec.0000.fil" && \
          -f "$output_dir/${target}.rawspec.0001.fil" && \
          -f "$output_dir/${target}.rawspec.0002.fil" ]]; then
        echo "Filterbank files 0000.fil, 0001.fil, and 0002.fil exist in $output_dir. Skipping rawspec..."
    else
        echo "Running rawspec..."
        run rawspec -f 65536,8,64 -t 54,16,3072 -p 1,1,4 "$output_dir/${target}"
        run chmod o+r "$output_dir"/*.fil 2>/dev/null || true
        run chown -R 1000:1000 "$output_dir"
    fi

    # ===== Plotting & Slack upload =====
    png_count=$(find "$output_dir" -maxdepth 1 -type f -name "*.png" 2>/dev/null | wc -l)
    if [[ "$png_count" -eq 0 ]]; then
        echo "No PNG plots found in $output_dir. Generating plots..."
        fil_count=$(find "$output_dir" -maxdepth 1 -type f -name "*.fil" 2>/dev/null | wc -l)
        if [[ "$fil_count" -eq 0 ]]; then
            echo "No .fil files found in $output_dir. Cannot generate plots. Skipping Slack upload."
        else
            for fil in "$output_dir"/*.fil; do
                [ -e "$fil" ] || continue
                run python "/datax2/projects/LOFTS/LOFTS-Scripts/pipeline/plot-bandpass.py" -f "$fil" -s "$station"
            done
            echo "Uploading plots to Slack..."
            run python "/datax2/projects/LOFTS/LOFTS-Scripts/pipeline/slack-bandpass.py" "$output_dir"
            run chmod o+r "$output_dir"/*.png 2>/dev/null || true
            run chown -R 1000:1000 "$output_dir"
        fi
    else
        echo "Found $png_count PNG plot(s) in $output_dir. Skipping plotting and Slack upload."
    fi

    # ===== Cleanup raws if .fils exist =====
    if [[ -f "$output_dir/${target}.rawspec.0000.fil" && \
          -f "$output_dir/${target}.rawspec.0001.fil" && \
          -f "$output_dir/${target}.rawspec.0002.fil" ]]; then
        echo "Cleaning raw files..."
        run rm -f "$output_dir/${target}"*.raw
    fi

    run chmod o+r "$output_dir"/*.fil 2>/dev/null || true
    run chown -R 1000:1000 "$output_dir"

done

echo "===== Script finished at $(date) ====="

} 2> >(tee -a "$error_file" >&2) | tee -a "$log_file"

echo "Log written to: $log_file"
echo "Errors written to: $error_file"