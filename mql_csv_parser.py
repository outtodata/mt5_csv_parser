import argparse
import glob
import os
import sys
import pandas as pd


def process_mql_file(file_path, keep_columns=None, drop_columns=None):
    """Processes a single MT5 CSV export file (Bars or Ticks) with comprehensive error handling."""
    if not os.path.exists(file_path):
        print(f"Error: File not found: {file_path}")
        return False

    print(f"Processing: {file_path}")

    try:
        # 1. Detect delimiter (\t or ,)
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            first_line = f.readline()
        separator = "\t" if "\t" in first_line else ","

        # 2. Read the file
        df = pd.read_csv(file_path, sep=separator, low_memory=False)

        # 3. Basic structure validation
        required = ["<DATE>", "<TIME>"]
        if not all(col in df.columns for col in required):
            print(
                f"Skipping {file_path}: Missing <DATE> or <TIME> columns. Is this a valid MT5 export?"
            )
            return False

        # 4. Parse and set DateTime index
        df["Date"] = pd.to_datetime(
            df["<DATE>"] + " " + df["<TIME>"], format="mixed"
        )
        df.set_index("Date", inplace=True)
        df.drop(columns=["<DATE>", "<TIME>"], errors="ignore", inplace=True)

        # 5. Clean up column names (remove brackets and capitalize)
        df.columns = [
            col.replace("<", "").replace(">", "").capitalize()
            for col in df.columns
        ]

        # 6. Check if this is a Tick Data file or Bar Data file
        is_tick_data = any(col in df.columns for col in ["Bid", "Ask", "Last"])

        if is_tick_data:
            # TICK DATA SPECIFIC LOGIC
            # Drop ONLY columns that are completely empty (all values are NaN)
            df.dropna(how="all", axis=1, inplace=True)

            # Forward fill and backward fill existing columns to handle missing data between updates
            df.ffill(inplace=True)
            df.bfill(inplace=True)

            # Normalize volume column name for ticks if needed
            if "Volume" not in df.columns and "Tickvol" in df.columns:
                df.rename(columns={"Tickvol": "Volume"}, inplace=True)

            default_trash = []
        else:
            # BAR DATA SPECIFIC LOGIC
            if "Tickvol" in df.columns:
                df.rename(columns={"Tickvol": "Volume"}, inplace=True)
            default_trash = ["Vol", "Spread"]

        # 7. Column filtering logic (Only runs if user explicitly provided flags)
        if keep_columns:
            keep_cols = [c.capitalize() for c in keep_columns]
            # Dynamic base columns depending on what survived the empty column drop
            base_cols = (
                [c for c in ["Bid", "Ask", "Last", "Volume"] if c in df.columns]
                if is_tick_data
                else ["Open", "High", "Low", "Close", "Volume"]
            )
            allowed_cols = list(set(base_cols + keep_cols))
            cols_to_drop = [c for c in df.columns if c not in allowed_cols]
            df.drop(columns=cols_to_drop, errors="ignore", inplace=True)
        elif drop_columns:
            drop_cols = [c.capitalize() for c in drop_columns]
            df.drop(columns=drop_cols, errors="ignore", inplace=True)
        else:
            # If no CLI flags are used, we do NOT strictly limit columns anymore.
            # We only drop default_trash for Bar Data if it exists.
            if default_trash:
                df.drop(columns=default_trash, errors="ignore", inplace=True)

        # 8. Drop remaining NaNs (safe now since completely empty columns are gone)
        df.dropna(inplace=True)

        # 9. Overwrite the original file
        df.to_csv(file_path)
        print(f"Successfully processed: {file_path}")
        print(f"   Data type detected: {'Tick Data' if is_tick_data else 'Bar Data'}")
        print(f"   Output columns: {list(df.columns)}")
        print(f"   Total rows: {len(df)}\n")
        return True

    except Exception as e:
        print(f"Critical error while processing {file_path}: {e}\n")
        return False


def main():
    parser = argparse.ArgumentParser(
        description="Monolithic CLI parser for MetaTrader 5 (MQL5) CSV data exports (Bars and Ticks)."
    )
    parser.add_argument(
        "files",
        nargs="+",
        help="Path to one or more CSV files (wildcards like *.csv are supported)",
    )

    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--keep",
        nargs="+",
        metavar="COL",
        help="Keep ONLY specified custom columns in addition to basic data. Example: --keep flags",
    )
    group.add_argument(
        "--drop",
        nargs="+",
        metavar="COL",
        help="Force drop specific columns. Example: --drop flags",
    )

    args = parser.parse_args()

    target_files = []
    for f_pattern in args.files:
        matched = glob.glob(f_pattern)
        if matched:
            target_files.extend(matched)
        else:
            target_files.append(f_pattern)

    target_files = list(set(target_files))

    print(f"Found {len(target_files)} file(s) to process...\n")

    success_count = 0
    for file in target_files:
        if process_mql_file(
            file, keep_columns=args.keep, drop_columns=args.drop
        ):
            success_count += 1

    print(
        f"Done! Successfully processed {success_count}/{len(target_files)} file(s)."
    )


if __name__ == "__main__":
    main()