import argparse

from bootstrap import run_bootstrap
from replay import run_replay


def main():
    parser = argparse.ArgumentParser(description="Bootstrap and replay Olist data")
    parser.add_argument("--data-dir", required=True)
    parser.add_argument("--dsn", required=True)
    parser.add_argument("--limit", type=int, help="Number of orders to replay")
    parser.add_argument("--chunk-size", type=int, default=5000)
    parser.add_argument("--speed", type=float, default=0.0, help="Source seconds per real second; 0 runs immediately")
    parser.add_argument("--log-every", type=int, default=1000, help="Log replay progress every N events; 0 disables progress logs")

    args = parser.parse_args()

    run_bootstrap(args.data_dir, args.dsn, chunk_size=args.chunk_size)
    run_replay(args.data_dir, args.dsn, args.limit, args.speed, args.log_every)


if __name__ == "__main__":
    main()
