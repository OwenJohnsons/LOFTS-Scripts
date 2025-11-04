import argparse

def calculate_resolutions(t, f, bandwidth, coarse_channels, block_channels):

    bandwidth = bandwidth * 1e6

    if block_channels%f != 0:
        print(f"Number of fine channels ({f}) must be a factor of the number of channels in a GUPPI RAW block ({block_channels})")
        exit(1)
    
    else: 
        block_chans_per_fine = block_channels / f
        if (block_chans_per_fine % t != 0) and (t % block_chans_per_fine != 0):
            print(f"Number of integrations ({t}) must be a factor or a multiple of the number of blocks in a time series ({block_chans_per_fine})")
            exit(1)

    # Frequency resolution in Hz
    f_res = (bandwidth / coarse_channels) / f
    
    # Time resolution in seconds
    t_res = 5.12e-6 * f * t

    print(f"Bandwidth: {bandwidth/1e6} MHz")
    print(f"Coarse Channels: {coarse_channels}")
    print(f"Coarse Channel Resolution: {(bandwidth / coarse_channels)/1000} KHz")

    return f_res, t_res

def main():
    parser = argparse.ArgumentParser(description="Calculate frequency and time resolution")
    
    parser.add_argument('-f', '--fine_channels', type=int, required=True, help="Number of fine channels")
    parser.add_argument('-t', '--integrations', type=int, required=True, help="Number of integrations")
    parser.add_argument('--bandwidth', type=float, default=90.0, help="Total bandwidth in MHz (default: 90 MHz)")
    parser.add_argument('--coarse_channels', type=int, default=412, help="Number of coarse channels (default: 412)")
    parser.add_argument('--block_channels', type=int, default=65536, help="Number of channels in GUPPI RAW block (default:65536)")
    
    args = parser.parse_args()
    
    f_res, t_res = calculate_resolutions(args.integrations, args.fine_channels, args.bandwidth, args.coarse_channels, args.block_channels)
    
    # Output the results
    print(f"Frequency Resolution: {f_res:.6f} Hz")
    print(f"Time Resolution: {t_res:.6f} seconds")

if __name__ == "__main__":
    main()
