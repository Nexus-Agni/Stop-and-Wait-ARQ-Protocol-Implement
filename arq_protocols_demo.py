"""
ARQ Protocols Comparison and Main Demonstration
==============================================
This module provides a comprehensive comparison of all three ARQ protocols:
- Stop-and-Wait ARQ
- Go-Back-N ARQ  
- Selective Repeat ARQ

It demonstrates their differences in efficiency, complexity, and behavior.
"""

import time
import random
from stop_and_wait import StopAndWaitSender, StopAndWaitReceiver
from go_back_n import GoBackNSender, GoBackNReceiver
from selective_repeat import SelectiveRepeatSender, SelectiveRepeatReceiver

def compare_protocols():
    """Compare all three ARQ protocols with the same test data"""
    print("=" * 80)
    print("ARQ PROTOCOLS COMPARISON SIMULATION")
    print("=" * 80)
    
    # Common test parameters
    test_data = ["Data1", "Data2", "Data3", "Data4", "Data5", 
                "Data6", "Data7", "Data8", "Data9", "Data10"]
    window_size = 4
    
    # Set the same random seed for fair comparison
    protocols_results = {}
    
    print(f"🧪 Testing with {len(test_data)} frames")
    print(f"🧪 Window size for windowed protocols: {window_size}")
    print(f"🧪 Simulated conditions: 10% corruption, 15% loss, 10% ACK loss")
    
    # Test Stop-and-Wait
    print("\n" + "="*60)
    print("TESTING STOP-AND-WAIT ARQ")
    print("="*60)
    
    random.seed(42)  # Reset seed for each test
    start_time = time.time()
    
    sw_sender = StopAndWaitSender(timeout=1.0)
    sw_receiver = StopAndWaitReceiver()
    
    successful = 0
    for data in test_data:
        if sw_sender.send_frame(data, sw_receiver):
            successful += 1
        time.sleep(0.1)
    
    sw_time = time.time() - start_time
    sw_stats = sw_sender.get_statistics()
    
    protocols_results['Stop-and-Wait'] = {
        'time': sw_time,
        'successful': successful,
        'total_frames': len(test_data),
        'transmissions': sw_stats['total_transmissions'],
        'efficiency': sw_stats['efficiency'],
        'received_data': len(sw_receiver.get_received_data())
    }
    
    # Test Go-Back-N
    print("\n" + "="*60)
    print("TESTING GO-BACK-N ARQ")
    print("="*60)
    
    random.seed(42)  # Reset seed for each test
    start_time = time.time()
    
    gbn_sender = GoBackNSender(window_size=window_size, timeout=1.0)
    gbn_receiver = GoBackNReceiver()
    
    gbn_sender.add_data(test_data.copy())
    gbn_sender.send_frames(gbn_receiver)
    
    gbn_time = time.time() - start_time
    gbn_stats = gbn_sender.get_statistics()
    gbn_recv_stats = gbn_receiver.get_statistics()
    
    protocols_results['Go-Back-N'] = {
        'time': gbn_time,
        'successful': gbn_recv_stats['frames_accepted'],
        'total_frames': len(test_data),
        'transmissions': gbn_stats['total_transmissions'],
        'retransmissions': gbn_stats['retransmissions'],
        'efficiency': gbn_stats['efficiency'],
        'received_data': len(gbn_receiver.get_received_data())
    }
    
    # Test Selective Repeat
    print("\n" + "="*60)
    print("TESTING SELECTIVE REPEAT ARQ")
    print("="*60)
    
    random.seed(42)  # Reset seed for each test
    start_time = time.time()
    
    sr_sender = SelectiveRepeatSender(window_size=window_size, timeout=1.0)
    sr_receiver = SelectiveRepeatReceiver(window_size=window_size)
    
    sr_sender.add_data(test_data.copy())
    sr_sender.send_frames(sr_receiver)
    
    sr_time = time.time() - start_time
    sr_stats = sr_sender.get_statistics()
    sr_recv_stats = sr_receiver.get_statistics()
    
    protocols_results['Selective Repeat'] = {
        'time': sr_time,
        'successful': sr_recv_stats['frames_delivered'],
        'total_frames': len(test_data),
        'transmissions': sr_stats['total_transmissions'],
        'retransmissions': sr_stats['retransmissions'],
        'efficiency': sr_stats['efficiency'],
        'received_data': len(sr_receiver.get_received_data())
    }
    
    # Display comparison results
    print("\n" + "="*80)
    print("PROTOCOL COMPARISON RESULTS")
    print("="*80)
    
    print(f"{'Protocol':<20} {'Time(s)':<10} {'Success':<10} {'Transmit':<10} {'Retrans':<10} {'Efficiency':<12}")
    print("-" * 80)
    
    for protocol, results in protocols_results.items():
        retrans = results.get('retransmissions', 'N/A')
        print(f"{protocol:<20} {results['time']:<10.2f} {results['successful']:<10} "
              f"{results['transmissions']:<10} {retrans:<10} {results['efficiency']:<12}")
    
    # Analysis
    print("\n" + "="*80)
    print("ANALYSIS")
    print("="*80)
    
    fastest = min(protocols_results.items(), key=lambda x: x[1]['time'])
    most_efficient = min(protocols_results.items(), 
                        key=lambda x: x[1]['transmissions'])
    
    print(f"🏆 Fastest Protocol: {fastest[0]} ({fastest[1]['time']:.2f}s)")
    print(f"🏆 Most Efficient: {most_efficient[0]} ({most_efficient[1]['transmissions']} transmissions)")
    
    print(f"\n📊 Protocol Characteristics Summary:")
    print(f"   Stop-and-Wait: Simple, reliable, but slow (1 frame at a time)")
    print(f"   Go-Back-N: Faster than S&W, but retransmits good frames on error")
    print(f"   Selective Repeat: Most efficient, complex implementation")
    
    return protocols_results

def demonstrate_error_scenarios():
    """Demonstrate how each protocol handles different error scenarios"""
    print("\n" + "="*80)
    print("ERROR SCENARIO DEMONSTRATIONS")
    print("="*80)
    
    scenarios = [
        {"name": "Low Error Rate", "corruption": 0.05, "loss": 0.05, "ack_loss": 0.05},
        {"name": "Medium Error Rate", "corruption": 0.15, "loss": 0.15, "ack_loss": 0.10},
        {"name": "High Error Rate", "corruption": 0.25, "loss": 0.25, "ack_loss": 0.15}
    ]
    
    for scenario in scenarios:
        print(f"\n📊 Scenario: {scenario['name']}")
        print(f"   Corruption: {scenario['corruption']*100}%, Loss: {scenario['loss']*100}%, ACK Loss: {scenario['ack_loss']*100}%")
        print("-" * 50)
        
        # This would require modifying the error rates in the classes
        # For now, we'll just show the concept
        print("   💡 Expected behavior:")
        print("   • Stop-and-Wait: Linear increase in retransmissions")
        print("   • Go-Back-N: Exponential increase due to cascading retransmissions")  
        print("   • Selective Repeat: Minimal increase, only lost frames retransmitted")

def show_protocol_features():
    """Display detailed feature comparison"""
    print("\n" + "="*80)
    print("PROTOCOL FEATURES COMPARISON")
    print("="*80)
    
    features = [
        ["Feature", "Stop-and-Wait", "Go-Back-N", "Selective Repeat"],
        ["-" * 20, "-" * 15, "-" * 12, "-" * 17],
        ["Window Size", "1", "N (4-8 typical)", "N (sender & receiver)"],
        ["Sequence Numbers", "0,1 (2 total)", "0 to N-1", "0 to 2N-1"],
        ["Buffer Required", "1 frame", "N frames (sender)", "N frames (both ends)"],
        ["Acknowledgment", "Cumulative", "Cumulative", "Individual"],
        ["Retransmission", "Single frame", "From error point", "Selective frames"],
        ["Out-of-order", "Not handled", "Discarded", "Buffered"],
        ["Complexity", "Simple", "Medium", "Complex"],
        ["Efficiency", "Low", "Medium", "High"],
        ["Best Use Case", "Noisy channels", "Good channels", "High-speed links"]
    ]
    
    for row in features:
        print(f"{row[0]:<20} {row[1]:<15} {row[2]:<12} {row[3]:<17}")

def main():
    """Main demonstration function"""
    print("🌟 Welcome to ARQ Protocols Simulation Suite!")
    print("This demonstration will show you the working of three important ARQ protocols.")
    
    while True:
        print("\n" + "="*60)
        print("MENU - ARQ PROTOCOLS SIMULATION")
        print("="*60)
        print("1. Run Stop-and-Wait ARQ simulation")
        print("2. Run Go-Back-N ARQ simulation") 
        print("3. Run Selective Repeat ARQ simulation")
        print("4. Compare all protocols")
        print("5. Show protocol features comparison")
        print("6. Show error scenario analysis")
        print("7. Exit")
        
        choice = input("\nEnter your choice (1-7): ").strip()
        
        if choice == '1':
            from stop_and_wait import demonstrate_stop_and_wait
            demonstrate_stop_and_wait()
            
        elif choice == '2':
            from go_back_n import demonstrate_go_back_n
            demonstrate_go_back_n()
            
        elif choice == '3':
            from selective_repeat import demonstrate_selective_repeat
            demonstrate_selective_repeat()
            
        elif choice == '4':
            compare_protocols()
            
        elif choice == '5':
            show_protocol_features()
            
        elif choice == '6':
            demonstrate_error_scenarios()
            
        elif choice == '7':
            print("\n👋 Thank you for exploring ARQ protocols!")
            print("Key takeaways:")
            print("• Stop-and-Wait: Simple but inefficient")
            print("• Go-Back-N: Good balance of simplicity and efficiency")
            print("• Selective Repeat: Most efficient but most complex")
            break
            
        else:
            print("❌ Invalid choice. Please enter 1-7.")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    main()
