#!/bin/bash
# TCP Optimization Script for Linux (MinhOS PC)
# Run as root or with sudo

echo "============================================"
echo "TCP Optimization for MinhOS v3"
echo "============================================"
echo

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (sudo $0)"
    exit 1
fi

# Backup current sysctl settings
echo "Backing up current settings..."
cp /etc/sysctl.conf /etc/sysctl.conf.backup.$(date +%Y%m%d_%H%M%S)

# Create optimized sysctl configuration
cat > /etc/sysctl.d/99-minh-tcp-optimizations.conf << 'EOF'
# MinhOS v3 TCP optimizations for real-time streaming
# Created: $(date)

# Disable Nagle's Algorithm and optimize for low latency
net.ipv4.tcp_nodelay = 1
net.ipv4.tcp_low_latency = 1

# Enable advanced TCP features
net.ipv4.tcp_sack = 1
net.ipv4.tcp_timestamps = 1
net.ipv4.tcp_window_scaling = 1

# Optimize buffer sizes for better throughput
net.core.rmem_default = 262144
net.core.wmem_default = 262144
net.core.rmem_max = 16777216
net.core.wmem_max = 16777216

# TCP buffer sizes: min, default, max
net.ipv4.tcp_rmem = 4096 131072 16777216
net.ipv4.tcp_wmem = 4096 131072 16777216

# Reduce TIME_WAIT sockets for faster connection recycling
net.ipv4.tcp_fin_timeout = 15
net.ipv4.tcp_tw_reuse = 1

# Increase the maximum number of connections
net.core.somaxconn = 4096
net.ipv4.tcp_max_syn_backlog = 4096

# Enable TCP Fast Open for reduced latency
net.ipv4.tcp_fastopen = 3

# Disable TCP slow start after idle
net.ipv4.tcp_slow_start_after_idle = 0

# Set TCP congestion control algorithm to BBR if available
net.core.default_qdisc = fq
net.ipv4.tcp_congestion_control = bbr

# Keep-alive settings for persistent connections
net.ipv4.tcp_keepalive_time = 30
net.ipv4.tcp_keepalive_intvl = 10
net.ipv4.tcp_keepalive_probes = 3

EOF

echo "Applying TCP optimizations..."
sysctl -p /etc/sysctl.d/99-minh-tcp-optimizations.conf

# Verify BBR is available and loaded
if lsmod | grep -q tcp_bbr; then
    echo "BBR congestion control is active"
else
    echo "Loading BBR module..."
    modprobe tcp_bbr
    echo "tcp_bbr" >> /etc/modules-load.d/tcp_bbr.conf
fi

# Set network interface optimizations
INTERFACE=$(ip route | grep default | awk '{print $5}' | head -n1)
if [ -n "$INTERFACE" ]; then
    echo
    echo "Optimizing network interface: $INTERFACE"
    
    # Disable interrupt coalescing for lower latency
    ethtool -C $INTERFACE rx-usecs 0 tx-usecs 0 2>/dev/null || true
    
    # Set ring buffer sizes
    ethtool -G $INTERFACE rx 4096 tx 4096 2>/dev/null || true
    
    # Enable receive packet steering
    echo ffff > /sys/class/net/$INTERFACE/queues/rx-0/rps_cpus 2>/dev/null || true
fi

echo
echo "============================================"
echo "TCP optimizations applied successfully!"
echo
echo "Current TCP settings:"
echo "- TCP_NODELAY: $(sysctl -n net.ipv4.tcp_nodelay)"
echo "- TCP_LOW_LATENCY: $(sysctl -n net.ipv4.tcp_low_latency)"
echo "- Congestion Control: $(sysctl -n net.ipv4.tcp_congestion_control)"
echo
echo "No reboot required - changes are active immediately"
echo "============================================"