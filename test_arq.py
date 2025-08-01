"""
Quick Test Suite for ARQ Protocols
==================================
This script runs quick tests to verify all protocols work correctly.
"""

import sys
import time
import random
from io import StringIO

def capture_output(func, *args, **kwargs):
    """Capture function output for testing"""
    old_stdout = sys.stdout
    sys.stdout = captured_output = StringIO()
    
    try:
        result = func(*args, **kwargs)
        output = captured_output.getvalue()
        return result, output
    finally:
        sys.stdout = old_stdout

def test_stop_and_wait():
    """Test Stop-and-Wait protocol"""
    print("🧪 Testing Stop-and-Wait ARQ...")
    
    try:
        from stop_and_wait import StopAndWaitSender, StopAndWaitReceiver
        
        # Set deterministic seed
        random.seed(123)
        
        sender = StopAndWaitSender(timeout=0.1)
        receiver = StopAndWaitReceiver()
        
        # Test with simple data
        test_data = ["Test1", "Test2", "Test3"]
        successful = 0
        
        for data in test_data:
            if sender.send_frame(data, receiver):
                successful += 1
            time.sleep(0.01)  # Small delay
        
        stats = sender.get_statistics()
        received_data = receiver.get_received_data()
        
        print(f"   ✅ Sent: {len(test_data)}, Received: {len(received_data)}")
        print(f"   ✅ Total transmissions: {stats['total_transmissions']}")
        print(f"   ✅ Efficiency: {stats['efficiency']}")
        
        return len(received_data) > 0
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_go_back_n():
    """Test Go-Back-N protocol"""
    print("🧪 Testing Go-Back-N ARQ...")
    
    try:
        from go_back_n import GoBackNSender, GoBackNReceiver
        
        # Set deterministic seed
        random.seed(123)
        
        sender = GoBackNSender(window_size=3, timeout=0.1)
        receiver = GoBackNReceiver()
        
        # Test with simple data
        test_data = ["Frame1", "Frame2", "Frame3", "Frame4"]
        sender.add_data(test_data)
        
        # Capture output to avoid cluttering test results
        result, output = capture_output(sender.send_frames, receiver)
        
        stats = sender.get_statistics()
        recv_stats = receiver.get_statistics()
        received_data = receiver.get_received_data()
        
        print(f"   ✅ Sent: {len(test_data)}, Received: {len(received_data)}")
        print(f"   ✅ Total transmissions: {stats['total_transmissions']}")
        print(f"   ✅ Retransmissions: {stats['retransmissions']}")
        print(f"   ✅ Frames accepted: {recv_stats['frames_accepted']}")
        
        return len(received_data) > 0
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_selective_repeat():
    """Test Selective Repeat protocol"""
    print("🧪 Testing Selective Repeat ARQ...")
    
    try:
        from selective_repeat import SelectiveRepeatSender, SelectiveRepeatReceiver
        
        # Set deterministic seed
        random.seed(123)
        
        sender = SelectiveRepeatSender(window_size=3, timeout=0.1)
        receiver = SelectiveRepeatReceiver(window_size=3)
        
        # Test with simple data
        test_data = ["Alpha", "Beta", "Gamma", "Delta"]
        sender.add_data(test_data)
        
        # Capture output to avoid cluttering test results
        result, output = capture_output(sender.send_frames, receiver)
        
        stats = sender.get_statistics()
        recv_stats = receiver.get_statistics()
        received_data = receiver.get_received_data()
        
        print(f"   ✅ Sent: {len(test_data)}, Delivered: {len(received_data)}")
        print(f"   ✅ Total transmissions: {stats['total_transmissions']}")
        print(f"   ✅ Retransmissions: {stats['retransmissions']}")
        print(f"   ✅ Frames delivered: {recv_stats['frames_delivered']}")
        
        return len(received_data) > 0
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_main_demo():
    """Test main demo import"""
    print("🧪 Testing main demo module...")
    
    try:
        from arq_protocols_demo import compare_protocols, show_protocol_features
        
        print("   ✅ Main demo module imports successfully")
        print("   ✅ Core functions available")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def test_analysis_module():
    """Test analysis module"""
    print("🧪 Testing analysis module...")
    
    try:
        from arq_analysis import ARQAnalyzer
        
        analyzer = ARQAnalyzer()
        
        # Test error rate analysis
        result, output = capture_output(analyzer.analyze_error_rate_impact, [0.1, 0.2])
        
        print("   ✅ Analysis module imports successfully")
        print("   ✅ Error rate analysis works")
        
        return True
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("ARQ PROTOCOLS - QUICK TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Stop-and-Wait", test_stop_and_wait),
        ("Go-Back-N", test_go_back_n),
        ("Selective Repeat", test_selective_repeat),
        ("Main Demo", test_main_demo),
        ("Analysis Module", test_analysis_module)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name} Test:")
        print("-" * 40)
        
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"   ❌ Unexpected error: {e}")
            results[test_name] = False
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST RESULTS SUMMARY")
    print("=" * 60)
    
    passed = sum(results.values())
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name:<20} {status}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The ARQ protocols simulation is ready to use.")
        print("\n🚀 Quick start:")
        print("   python arq_protocols_demo.py")
    else:
        print("⚠️  Some tests failed. Please check the error messages above.")
    
    return passed == total

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
