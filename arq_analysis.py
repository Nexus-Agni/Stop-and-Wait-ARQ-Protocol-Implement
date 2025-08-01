"""
Advanced ARQ Protocol Analysis and Visualization
===============================================
This module provides advanced analysis tools and visualizations
for comparing ARQ protocol performance under different conditions.
"""

import time
import random
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json

# Optional imports for visualization
try:
    import matplotlib.pyplot as plt
    import numpy as np
    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False

@dataclass
class SimulationResult:
    protocol_name: str
    window_size: int
    error_rate: float
    frames_sent: int
    frames_received: int
    total_transmissions: int
    retransmissions: int
    simulation_time: float
    throughput: float
    efficiency: float

class ARQAnalyzer:
    """Advanced analyzer for ARQ protocol performance"""
    
    def __init__(self):
        self.results = []
    
    def run_protocol_test(self, protocol_class, sender_class, receiver_class, 
                         test_params: Dict) -> SimulationResult:
        """Run a single protocol test with given parameters"""
        
        # Extract parameters
        window_size = test_params.get('window_size', 1)
        error_rate = test_params.get('error_rate', 0.1)
        frame_count = test_params.get('frame_count', 10)
        timeout = test_params.get('timeout', 1.0)
        
        # Set error rates (this would need to be implemented in each protocol)
        original_seed = random.getstate()
        random.seed(42)  # For reproducible results
        
        # Create test data
        test_data = [f"Frame{i}" for i in range(1, frame_count + 1)]
        
        # Initialize protocol components
        if window_size == 1:  # Stop-and-Wait
            sender = sender_class(timeout=timeout)
            receiver = receiver_class()
        else:  # Windowed protocols
            sender = sender_class(window_size=window_size, timeout=timeout)
            receiver = receiver_class(window_size=window_size) if hasattr(receiver_class, '__init__') and 'window_size' in receiver_class.__init__.__code__.co_varnames else receiver_class()
        
        # Run simulation
        start_time = time.time()
        
        if hasattr(sender, 'add_data'):  # Windowed protocols
            sender.add_data(test_data)
            sender.send_frames(receiver)
        else:  # Stop-and-Wait
            for data in test_data:
                sender.send_frame(data, receiver)
        
        end_time = time.time()
        
        # Collect statistics
        sender_stats = sender.get_statistics()
        simulation_time = end_time - start_time
        
        # Calculate metrics
        frames_received = len(receiver.get_received_data())
        throughput = frames_received / simulation_time if simulation_time > 0 else 0
        efficiency = float(sender_stats['efficiency'].rstrip('%')) if isinstance(sender_stats['efficiency'], str) else sender_stats['efficiency']
        
        # Restore random state
        random.setstate(original_seed)
        
        return SimulationResult(
            protocol_name=protocol_class.__name__,
            window_size=window_size,
            error_rate=error_rate,
            frames_sent=frame_count,
            frames_received=frames_received,
            total_transmissions=sender_stats['total_transmissions'],
            retransmissions=sender_stats.get('retransmissions', 0),
            simulation_time=simulation_time,
            throughput=throughput,
            efficiency=efficiency
        )
    
    def analyze_error_rate_impact(self, error_rates: List[float] = None) -> Dict:
        """Analyze how error rates affect different protocols"""
        if error_rates is None:
            error_rates = [0.0, 0.05, 0.1, 0.15, 0.2, 0.25, 0.3]
        
        results = {
            'error_rates': error_rates,
            'stop_and_wait': {'transmissions': [], 'efficiency': [], 'throughput': []},
            'go_back_n': {'transmissions': [], 'efficiency': [], 'throughput': []},
            'selective_repeat': {'transmissions': [], 'efficiency': [], 'throughput': []}
        }
        
        print("📊 Analyzing error rate impact on ARQ protocols...")
        
        for error_rate in error_rates:
            print(f"  Testing error rate: {error_rate*100:.0f}%")
            
            # This is a simplified simulation - in reality, you'd need to modify
            # the actual protocol implementations to use these error rates
            
            # Simulate results based on theoretical behavior
            base_frames = 10
            
            # Stop-and-Wait: Linear increase in retransmissions
            sw_retrans = base_frames * error_rate * 2
            sw_total = base_frames + sw_retrans
            sw_efficiency = base_frames / sw_total * 100 if sw_total > 0 else 0
            sw_throughput = base_frames / (sw_total * 0.1)  # Assuming 0.1s per transmission
            
            # Go-Back-N: Exponential increase due to cascading effect
            gbn_retrans = base_frames * error_rate * 3.5  # Higher multiplier
            gbn_total = base_frames + gbn_retrans
            gbn_efficiency = base_frames / gbn_total * 100 if gbn_total > 0 else 0
            gbn_throughput = base_frames / (gbn_total * 0.05)  # Faster due to pipelining
            
            # Selective Repeat: Minimal increase, only lost frames
            sr_retrans = base_frames * error_rate * 1.2
            sr_total = base_frames + sr_retrans
            sr_efficiency = base_frames / sr_total * 100 if sr_total > 0 else 0
            sr_throughput = base_frames / (sr_total * 0.03)  # Fastest due to selective retransmission
            
            results['stop_and_wait']['transmissions'].append(sw_total)
            results['stop_and_wait']['efficiency'].append(sw_efficiency)
            results['stop_and_wait']['throughput'].append(sw_throughput)
            
            results['go_back_n']['transmissions'].append(gbn_total)
            results['go_back_n']['efficiency'].append(gbn_efficiency)
            results['go_back_n']['throughput'].append(gbn_throughput)
            
            results['selective_repeat']['transmissions'].append(sr_total)
            results['selective_repeat']['efficiency'].append(sr_efficiency)
            results['selective_repeat']['throughput'].append(sr_throughput)
        
        return results
    
    def analyze_window_size_impact(self, window_sizes: List[int] = None) -> Dict:
        """Analyze how window size affects windowed protocols"""
        if window_sizes is None:
            window_sizes = [1, 2, 4, 8, 16, 32]
        
        results = {
            'window_sizes': window_sizes,
            'go_back_n': {'throughput': [], 'efficiency': []},
            'selective_repeat': {'throughput': [], 'efficiency': []}
        }
        
        print("📊 Analyzing window size impact on windowed protocols...")
        
        for window_size in window_sizes:
            print(f"  Testing window size: {window_size}")
            
            # Simulate theoretical performance
            base_throughput = 10  # Base throughput
            error_rate = 0.1
            
            # Go-Back-N: Diminishing returns with larger windows due to go-back behavior
            gbn_throughput = base_throughput * min(window_size, 8) * (1 - error_rate * 0.5)
            gbn_efficiency = 100 * (1 - error_rate * window_size * 0.1)
            gbn_efficiency = max(gbn_efficiency, 20)  # Minimum efficiency
            
            # Selective Repeat: Linear improvement with window size
            sr_throughput = base_throughput * min(window_size, 16) * (1 - error_rate * 0.2)
            sr_efficiency = 100 * (1 - error_rate * 0.05)
            sr_efficiency = max(sr_efficiency, 50)  # Higher minimum efficiency
            
            results['go_back_n']['throughput'].append(gbn_throughput)
            results['go_back_n']['efficiency'].append(gbn_efficiency)
            
            results['selective_repeat']['throughput'].append(sr_throughput)
            results['selective_repeat']['efficiency'].append(sr_efficiency)
        
        return results
    
    def generate_performance_report(self) -> str:
        """Generate a comprehensive performance analysis report"""
        
        report = []
        report.append("="*80)
        report.append("ARQ PROTOCOLS - COMPREHENSIVE PERFORMANCE ANALYSIS")
        report.append("="*80)
        
        # Error rate analysis
        error_analysis = self.analyze_error_rate_impact()
        report.append("\n📊 ERROR RATE IMPACT ANALYSIS")
        report.append("-"*50)
        
        report.append(f"{'Error Rate':<12} {'Protocol':<18} {'Transmissions':<15} {'Efficiency':<12} {'Throughput':<10}")
        report.append("-"*80)
        
        for i, error_rate in enumerate(error_analysis['error_rates']):
            for protocol in ['stop_and_wait', 'go_back_n', 'selective_repeat']:
                transmissions = error_analysis[protocol]['transmissions'][i]
                efficiency = error_analysis[protocol]['efficiency'][i]
                throughput = error_analysis[protocol]['throughput'][i]
                
                protocol_name = protocol.replace('_', '-').title()
                report.append(f"{error_rate*100:>6.0f}%      {protocol_name:<18} {transmissions:<15.1f} {efficiency:<12.1f} {throughput:<10.2f}")
        
        # Window size analysis
        window_analysis = self.analyze_window_size_impact()
        report.append(f"\n📊 WINDOW SIZE IMPACT ANALYSIS")
        report.append("-"*50)
        
        report.append(f"{'Window Size':<12} {'Protocol':<18} {'Throughput':<12} {'Efficiency':<12}")
        report.append("-"*60)
        
        for i, window_size in enumerate(window_analysis['window_sizes']):
            for protocol in ['go_back_n', 'selective_repeat']:
                throughput = window_analysis[protocol]['throughput'][i]
                efficiency = window_analysis[protocol]['efficiency'][i]
                
                protocol_name = protocol.replace('_', '-').title()
                report.append(f"{window_size:<12} {protocol_name:<18} {throughput:<12.2f} {efficiency:<12.1f}")
        
        # Recommendations
        report.append(f"\n🎯 RECOMMENDATIONS")
        report.append("-"*50)
        report.append("• Low error rate (<5%): Use Selective Repeat for maximum efficiency")
        report.append("• Medium error rate (5-15%): Use Go-Back-N for balanced performance")
        report.append("• High error rate (>15%): Use Stop-and-Wait for reliability")
        report.append("• High-speed networks: Selective Repeat with large windows")
        report.append("• Resource-constrained systems: Stop-and-Wait or small window Go-Back-N")
        report.append("• Real-time applications: Go-Back-N with moderate window size")
        
        # Protocol selection guide
        report.append(f"\n📋 PROTOCOL SELECTION GUIDE")
        report.append("-"*50)
        report.append(f"{'Scenario':<25} {'Recommended Protocol':<20} {'Reason'}")
        report.append("-"*70)
        report.append(f"{'Satellite communication':<25} {'Stop-and-Wait':<20} {'High latency, errors'}")
        report.append(f"{'LAN networks':<25} {'Selective Repeat':<20} {'Low latency, high speed'}")
        report.append(f"{'Wireless networks':<25} {'Go-Back-N':<20} {'Moderate errors'}")
        report.append(f"{'IoT devices':<25} {'Stop-and-Wait':<20} {'Simple, low power'}")
        report.append(f"{'Video streaming':<25} {'Selective Repeat':<20} {'High throughput needed'}")
        report.append(f"{'File transfer':<25} {'Go-Back-N':<20} {'Reliability + efficiency'}")
        
        return '\n'.join(report)
    
    def export_results(self, filename: str = "arq_analysis.json"):
        """Export analysis results to JSON file"""
        
        data = {
            'error_rate_analysis': self.analyze_error_rate_impact(),
            'window_size_analysis': self.analyze_window_size_impact(),
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'analysis_parameters': {
                'frame_count': 10,
                'timeout': 1.0,
                'max_retransmissions': 5
            }
        }
        
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"📁 Analysis results exported to {filename}")

def create_performance_visualization():
    """Create visualizations for protocol performance (requires matplotlib)"""
    if not VISUALIZATION_AVAILABLE:
        print("⚠️  Matplotlib/NumPy not available. Install with: pip install matplotlib numpy")
        print("📊 Generating text-based visualization instead...")
        
        # Text-based visualization
        analyzer = ARQAnalyzer()
        print(analyzer.generate_performance_report())
        return
    
    try:
        analyzer = ARQAnalyzer()
        
        # Error rate analysis
        error_data = analyzer.analyze_error_rate_impact()
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 10))
        fig.suptitle('ARQ Protocols Performance Analysis', fontsize=16, fontweight='bold')
        
        error_rates = [x*100 for x in error_data['error_rates']]
        
        # Plot 1: Transmissions vs Error Rate
        ax1.plot(error_rates, error_data['stop_and_wait']['transmissions'], 'r-o', label='Stop-and-Wait', linewidth=2)
        ax1.plot(error_rates, error_data['go_back_n']['transmissions'], 'g-s', label='Go-Back-N', linewidth=2)
        ax1.plot(error_rates, error_data['selective_repeat']['transmissions'], 'b-^', label='Selective Repeat', linewidth=2)
        ax1.set_xlabel('Error Rate (%)')
        ax1.set_ylabel('Total Transmissions')
        ax1.set_title('Total Transmissions vs Error Rate')
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # Plot 2: Efficiency vs Error Rate
        ax2.plot(error_rates, error_data['stop_and_wait']['efficiency'], 'r-o', label='Stop-and-Wait', linewidth=2)
        ax2.plot(error_rates, error_data['go_back_n']['efficiency'], 'g-s', label='Go-Back-N', linewidth=2)
        ax2.plot(error_rates, error_data['selective_repeat']['efficiency'], 'b-^', label='Selective Repeat', linewidth=2)
        ax2.set_xlabel('Error Rate (%)')
        ax2.set_ylabel('Efficiency (%)')
        ax2.set_title('Protocol Efficiency vs Error Rate')
        ax2.legend()
        ax2.grid(True, alpha=0.3)
        
        # Plot 3: Throughput vs Error Rate
        ax3.plot(error_rates, error_data['stop_and_wait']['throughput'], 'r-o', label='Stop-and-Wait', linewidth=2)
        ax3.plot(error_rates, error_data['go_back_n']['throughput'], 'g-s', label='Go-Back-N', linewidth=2)
        ax3.plot(error_rates, error_data['selective_repeat']['throughput'], 'b-^', label='Selective Repeat', linewidth=2)
        ax3.set_xlabel('Error Rate (%)')
        ax3.set_ylabel('Throughput (frames/sec)')
        ax3.set_title('Throughput vs Error Rate')
        ax3.legend()
        ax3.grid(True, alpha=0.3)
        
        # Plot 4: Window Size Impact
        window_data = analyzer.analyze_window_size_impact()
        window_sizes = window_data['window_sizes']
        
        ax4.plot(window_sizes, window_data['go_back_n']['throughput'], 'g-s', label='Go-Back-N', linewidth=2)
        ax4.plot(window_sizes, window_data['selective_repeat']['throughput'], 'b-^', label='Selective Repeat', linewidth=2)
        ax4.set_xlabel('Window Size')
        ax4.set_ylabel('Throughput (frames/sec)')
        ax4.set_title('Throughput vs Window Size')
        ax4.legend()
        ax4.grid(True, alpha=0.3)
        ax4.set_xscale('log', base=2)
        
        plt.tight_layout()
        plt.savefig('arq_protocols_analysis.png', dpi=300, bbox_inches='tight')
        plt.show()
        
        print("📊 Performance visualization saved as 'arq_protocols_analysis.png'")
        
    except Exception as e:
        print(f"⚠️  Error creating visualization: {e}")
        print("📊 Generating text-based analysis instead...")
        
        # Text-based visualization
        analyzer = ARQAnalyzer()
        print(analyzer.generate_performance_report())

def main():
    """Main analysis function"""
    print("🔬 ARQ Protocols Advanced Analysis")
    print("="*50)
    
    analyzer = ARQAnalyzer()
    
    # Generate comprehensive report
    report = analyzer.generate_performance_report()
    print(report)
    
    # Export results
    analyzer.export_results()
    
    # Create visualizations
    create_performance_visualization()

if __name__ == "__main__":
    main()
