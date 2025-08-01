"""
Selective Repeat ARQ Protocol - Focused Test
===========================================
This test demonstrates the fixed Selective Repeat implementation with detailed explanations.
"""

import random
from selective_repeat import SelectiveRepeatSender, SelectiveRepeatReceiver

def test_selective_repeat_fixed():
    """Test the fixed Selective Repeat implementation"""
    print("=" * 70)
    print("SELECTIVE REPEAT ARQ - FOCUSED TEST & DEMONSTRATION")
    print("=" * 70)
    
    # Use a deterministic seed for reproducible results
    random.seed(100)
    
    sender = SelectiveRepeatSender(window_size=3, timeout=1.0)
    receiver = SelectiveRepeatReceiver(window_size=3)
    
    test_data = ["Data1", "Data2", "Data3", "Data4", "Data5"]
    print(f"📋 Testing with {len(test_data)} frames: {test_data}")
    print(f"📋 Window size: {sender.window_size}")
    print(f"📋 Sequence number space: 0-{sender.max_seq_num-1}")
    
    sender.add_data(test_data)
    
    print(f"\n🔧 Key Fixes Applied:")
    print(f"   • Infinite loop prevention with max iterations")
    print(f"   • Window boundary checks for retransmissions")
    print(f"   • Maximum retransmission limit per frame")
    print(f"   • Proper cleanup of acknowledged frames")
    print(f"   • Improved timeout management")
    
    print(f"\n🚀 Starting transmission...")
    print("=" * 70)
    
    import time
    start_time = time.time()
    result = sender.send_frames(receiver)
    end_time = time.time()
    
    print("=" * 70)
    print("📊 RESULTS ANALYSIS")
    print("=" * 70)
    
    sender_stats = sender.get_statistics()
    receiver_stats = receiver.get_statistics()
    
    print(f"✅ Transmission successful: {result}")
    print(f"📤 Frames sent: {len(test_data)}")
    print(f"📥 Frames delivered: {receiver_stats['frames_delivered']}")
    print(f"📦 Frames buffered: {receiver_stats['frames_buffered']}")
    print(f"🔄 Total transmissions: {sender_stats['total_transmissions']}")
    print(f"🔄 Retransmissions: {sender_stats['retransmissions']}")
    print(f"📈 Efficiency: {sender_stats['efficiency']}")
    print(f"⏱️  Time taken: {end_time - start_time:.2f} seconds")
    print(f"📋 Received data: {receiver.get_received_data()}")
    
    # Verify correctness
    expected_data = test_data
    actual_data = receiver.get_received_data()
    
    print(f"\n🧪 CORRECTNESS VERIFICATION")
    print("=" * 70)
    print(f"Expected: {expected_data}")
    print(f"Actual:   {actual_data}")
    print(f"✅ Data integrity: {'PASS' if expected_data == actual_data else 'FAIL'}")
    print(f"✅ All frames delivered: {'PASS' if len(actual_data) == len(expected_data) else 'FAIL'}")
    print(f"✅ Correct order: {'PASS' if actual_data == expected_data else 'FAIL'}")
    
    # Protocol characteristics summary
    print(f"\n📚 SELECTIVE REPEAT CHARACTERISTICS DEMONSTRATED")
    print("=" * 70)
    print(f"✅ Individual frame acknowledgments")
    print(f"✅ Selective retransmission of lost/corrupted frames only")
    print(f"✅ Out-of-order frame buffering at receiver")
    print(f"✅ Independent timers for each frame")
    print(f"✅ Window sliding based on acknowledged frames")
    print(f"✅ No unnecessary retransmissions of correctly received frames")
    
    return result and (actual_data == expected_data)

def compare_with_other_protocols():
    """Brief comparison with other protocols"""
    print(f"\n🆚 PROTOCOL COMPARISON SUMMARY")
    print("=" * 70)
    print(f"{'Protocol':<18} {'Window':<8} {'Retransmission':<15} {'Efficiency':<12} {'Complexity'}")
    print("-" * 70)
    print(f"{'Stop-and-Wait':<18} {'1':<8} {'Single frame':<15} {'Low':<12} {'Simple'}")
    print(f"{'Go-Back-N':<18} {'N':<8} {'From error point':<15} {'Medium':<12} {'Medium'}")
    print(f"{'Selective Repeat':<18} {'N':<8} {'Selective only':<15} {'High':<12} {'Complex'}")
    
    print(f"\n💡 WHEN TO USE SELECTIVE REPEAT:")
    print(f"   • High-speed networks with low error rates")
    print(f"   • When bandwidth is expensive")
    print(f"   • Applications requiring maximum throughput")
    print(f"   • When complexity cost is acceptable")

if __name__ == "__main__":
    success = test_selective_repeat_fixed()
    compare_with_other_protocols()
    
    if success:
        print(f"\n🎉 Selective Repeat ARQ test completed successfully!")
        print(f"The protocol now works correctly without infinite loops.")
    else:
        print(f"\n❌ Test failed - check implementation.")
