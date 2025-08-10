
#!/usr/bin/env bash

# Number of roscos to generate
dictionary=$1
N=$2

# Optional: output directory (default: current dir)
OUTDIR=${3:-.}

# Ensure the output directory exists
mkdir -p "$OUTDIR"

for ((i=1; i<=N; i++)); do
    echo "Generating rosco $i..."
    python3 pasapalabra/gen.py $1 > "$OUTDIR/rosco_$i.txt"
done

echo "✅ Generated $N roscos in $OUTDIR"
