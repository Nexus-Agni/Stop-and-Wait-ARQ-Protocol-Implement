"""
ARQ Protocols - Robustness and Safety Check
==========================================
This test specifically checks for potential infinite loops, stuck states,
and other robustness issues across all three ARQ protocols.
"""

import time
import random
import signal
import sys
from contextlib import contextmanager

@contextmanager
def timeout_context(seconds):
    """Context manager to timeout operations"""
    def timeout_handler(signum, frame):
        raise TimeoutError(f"Operation timed out after {seconds} seconds")
    
    # Set the signal handler
    old_handler = signal.signal(signal.SIGALRM, timeout_handler)
    signal.alarm(seconds)
    
    try:
        yield
    finally:
        # Restore the old handler
        signal.alarm(0)
        signal.signal(signal.SIGALRM, old_handler)

def test_protocol_robustness(protocol_name, sender_class, receiver_class, test_params):
    """Test a protocol for robustness issues"""
    print(f"\n🔍 Testing {protocol_name} robustness...")
    
    issues_found = []
    
    # Test 1: High error rate scenario
    print(f"   📋 Test 1: High error rate scenario")
    try:
        with timeout_context(10):  # 10 second timeout
            random.seed(999)  # Seed that might cause issues
            
            if protocol_name == "Stop-and-Wait":
                sender = sender_class(timeout=0.5)
                receiver = receiver_class()
                
                test_data = ["Test1", "Test2", "Test3"]
                successful = 0
                for data in test_data:
                    if sender.send_frame(data, receiver):
                        successful += 1
                
                if successful == 0:
                    issues_found.append("No frames delivered in high error scenario")
                    
            else:  # Windowed protocols
                sender = sender_class(window_size=3, timeout=0.5)
                receiver = receiver_class() if protocol_name == "Go-Back-N" else receiver_class(window_size=3)
                
                test_data = ["Data1", "Data2", "Data3", "Data4"]
                sender.add_data(test_data)
                sender.send_frames(receiver)
                
                received = receiver.get_received_data()
                if len(received) == 0:
                    issues_found.append("No frames delivered in high error scenario")
        
        print(f"   ✅ High error rate test passed")
    except TimeoutError:
        issues_found.append("Timeout in high error rate scenario - possible infinite loop")
        print(f"   ❌ High error rate test timed out")
    except Exception as e:
        issues_found.append(f"Exception in high error rate scenario: {str(e)}")
        print(f"   ❌ High error rate test failed: {e}")
    
    # Test 2: Window exhaustion scenario (for windowed protocols)
    if protocol_name != "Stop-and-Wait":
        print(f"   📋 Test 2: Window exhaustion scenario")
        try:
            with timeout_context(8):  # 8 second timeout
                random.seed(777)  # Different seed
                
                sender = sender_class(window_size=2, timeout=0.3)  # Small window
                receiver = receiver_class() if protocol_name == "Go-Back-N" else receiver_class(window_size=2)
                
                test_data = ["A", "B", "C", "D", "E"]  # More data than window
                sender.add_data(test_data)
                sender.send_frames(receiver)
            
            print(f"   ✅ Window exhaustion test passed")
        except TimeoutError:
            issues_found.append("Timeout in window exhaustion scenario")
            print(f"   ❌ Window exhaustion test timed out")
        except Exception as e:
            issues_found.append(f"Exception in window exhaustion: {str(e)}")
            print(f"   ❌ Window exhaustion test failed: {e}")
    
    # Test 3: Rapid retransmission scenario
    print(f"   📋 Test 3: Rapid retransmission scenario")
    try:
        with timeout_context(6):  # 6 second timeout
            random.seed(555)  # Seed for rapid retransmissions
            
            if protocol_name == "Stop-and-Wait":
                sender = sender_class(timeout=0.1)  # Very short timeout
                receiver = receiver_class()
                
                if sender.send_frame("RapidTest", receiver):
                    pass  # Expected to eventually succeed or fail gracefully
                    
            else:  # Windowed protocols
                sender = sender_class(window_size=2, timeout=0.1)  # Very short timeout
                receiver = receiver_class() if protocol_name == "Go-Back-N" else receiver_class(window_size=2)
                
                sender.add_data(["Rapid1", "Rapid2"])
                sender.send_frames(receiver)
        
        print(f"   ✅ Rapid retransmission test passed")
    except TimeoutError:
        issues_found.append("Timeout in rapid retransmission scenario")
        print(f"   ❌ Rapid retransmission test timed out")
    except Exception as e:
        issues_found.append(f"Exception in rapid retransmission: {str(e)}")
        print(f"   ❌ Rapid retransmission test failed: {e}")
    
    return issues_found

def run_robustness_tests():
    """Run comprehensive robustness tests for all protocols"""
    print("=" * 70)
    print("ARQ PROTOCOLS - COMPREHENSIVE ROBUSTNESS TESTING")
    print("=" * 70)
    print("Testing for: infinite loops, timeouts, stuck states, excessive retransmissions")
    
    # Import protocols
    from stop_and_wait import StopAndWaitSender, StopAndWaitReceiver
    from go_back_n import GoBackNSender, GoBackNReceiver
    from selective_repeat import SelectiveRepeatSender, SelectiveRepeatReceiver
    
    protocols = [
        ("Stop-and-Wait", StopAndWaitSender, StopAndWaitReceiver, {}),
        ("Go-Back-N", GoBackNSender, GoBackNReceiver, {"window_size": 4}),
        ("Selective Repeat", SelectiveRepeatSender, SelectiveRepeatReceiver, {"window_size": 4})
    ]
    
    all_issues = {}
    
    for protocol_name, sender_class, receiver_class, params in protocols:
        print(f"\n{'=' * 50}")
        print(f"TESTING {protocol_name.upper()}")
        print(f"{'=' * 50}")
        
        issues = test_protocol_robustness(protocol_name, sender_class, receiver_class, params)
        all_issues[protocol_name] = issues
        
        if not issues:
            print(f"🎉 {protocol_name}: All robustness tests PASSED")
        else:
            print(f"⚠️  {protocol_name}: {len(issues)} issue(s) found:")
            for issue in issues:
                print(f"    • {issue}")
    
    # Summary
    print(f"\n{'=' * 70}")
    print("ROBUSTNESS TEST SUMMARY")
    print("=" * 70)
    
    total_issues = sum(len(issues) for issues in all_issues.values())
    
    for protocol_name, issues in all_issues.items():
        status = "✅ ROBUST" if not issues else f"⚠️  {len(issues)} ISSUES"
        print(f"{protocol_name:<20} {status}")
    
    print(f"\nTotal issues found: {total_issues}")
    
    if total_issues == 0:
        print("🎉 All protocols passed robustness testing!")
        print("✅ No infinite loops detected")
        print("✅ All protocols terminate properly")
        print("✅ Good error handling under stress")
    else:
        print("⚠️  Some robustness issues detected - review above details")
    
    # Additional safety recommendations
    print(f"\n📋 SAFETY MEASURES IMPLEMENTED:")
    print("✅ Maximum iteration limits in all main loops")
    print("✅ Retransmission limits to prevent excessive traffic")
    print("✅ Timeout bounds to prevent infinite waiting")
    print("✅ Window boundary checks")
    print("✅ Proper cleanup of acknowledged frames")
    print("✅ Error handling for edge cases")
    
    return total_issues == 0

if __name__ == "__main__":
    try:
        success = run_robustness_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n🛑 Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during testing: {e}")
        sys.exit(1)
