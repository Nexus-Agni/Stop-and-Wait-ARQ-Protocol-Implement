"""
Go-Back-N ARQ Protocol Simulation
=================================
In this protocol:
- Sender can send N frames before needing ACK (sliding window)
- If a frame is lost, retransmit that frame and all subsequent frames
- Receiver only accepts frames in order
- More efficient than Stop-and-Wait but may retransmit correct frames
"""

import time
import random
import threading
from dataclasses import dataclass
from typing import List, Optional
from enum import Enum
from collections import deque

class FrameType(Enum):
    DATA = "DATA"
    ACK = "ACK"
    NAK = "NAK"

@dataclass
class Frame:
    seq_num: int
    frame_type: FrameType
    data: str = ""
    checksum: int = 0
    
    def __post_init__(self):
        if self.frame_type == FrameType.DATA:
            self.checksum = self.calculate_checksum()
    
    def calculate_checksum(self) -> int:
        """Simple checksum calculation"""
        return sum(ord(c) for c in self.data) % 256
    
    def is_corrupted(self) -> bool:
        """Simulate frame corruption during transmission"""
        return random.random() < 0.1  # 10% corruption rate

class GoBackNSender:
    def __init__(self, window_size: int = 4, timeout: float = 2.0):
        self.window_size = window_size
        self.timeout = timeout
        self.base = 0  # Base of the window
        self.next_seq_num = 0  # Next sequence number to use
        self.window = {}  # Sent but not acknowledged frames
        self.data_buffer = deque()  # Buffer for data to send
        self.max_seq_num = 8  # Sequence number space (0-7)
        self.total_transmissions = 0
        self.retransmissions = 0
        self.timer_active = False
        self.max_retransmissions = 10  # Maximum total retransmissions
        self.total_retransmission_count = 0  # Track total retransmissions
        
    def add_data(self, data_list: List[str]):
        """Add data to the buffer for transmission"""
        self.data_buffer.extend(data_list)
        print(f"📋 Sender: Added {len(data_list)} frames to buffer")
    
    def can_send(self) -> bool:
        """Check if we can send more frames"""
        return (self.next_seq_num < self.base + self.window_size and 
                len(self.data_buffer) > 0)
    
    def send_frames(self, receiver) -> bool:
        """Send frames using Go-Back-N protocol"""
        print(f"\n📤 Sender: Starting transmission with window size {self.window_size}")
        
        max_iterations = 500  # Prevent infinite loops
        iteration_count = 0
        
        while (self.data_buffer or self.window) and iteration_count < max_iterations:
            iteration_count += 1
            
            # Send new frames if window allows
            while self.can_send():
                data = self.data_buffer.popleft()
                frame = Frame(self.next_seq_num % self.max_seq_num, FrameType.DATA, data)
                
                print(f"📡 Sender: Sending frame {frame.seq_num} with data '{data}' "
                      f"(Window: {self.base % self.max_seq_num}-{(self.base + self.window_size - 1) % self.max_seq_num})")
                
                self.window[self.next_seq_num] = {
                    'frame': frame,
                    'timestamp': time.time(),
                    'data': data
                }
                
                self.total_transmissions += 1
                
                # Send to receiver
                ack_num = receiver.receive_frame(frame)
                
                if ack_num is not None:
                    self.process_ack(ack_num)
                
                self.next_seq_num += 1
                time.sleep(0.1)  # Small delay between transmissions
            
            # Check for timeouts (less frequently)
            if iteration_count % 3 == 0:  # Check every 3 iterations
                self.check_timeouts(receiver)
            
            # If no frames in window and no data to send, we're done
            if not self.window and not self.data_buffer:
                break
                
            time.sleep(0.05)  # Reduced sleep time
        
        if iteration_count >= max_iterations:
            print(f"⚠️ Sender: Maximum iterations reached, terminating")
        elif self.total_retransmission_count >= self.max_retransmissions:
            print(f"⚠️ Sender: Maximum retransmissions reached, terminating")
        
        print(f"✅ Sender: All frames transmitted successfully")
        return True
    
    def process_ack(self, ack_num: int):
        """Process received ACK"""
        print(f"✅ Sender: Received ACK for frame {ack_num}")
        
        # Remove acknowledged frames from window
        frames_to_remove = []
        for seq_num in list(self.window.keys()):
            if self.is_in_range(seq_num, self.base, ack_num):
                frames_to_remove.append(seq_num)
        
        for seq_num in frames_to_remove:
            if seq_num in self.window:  # Double-check existence
                del self.window[seq_num]
        
        # Update base
        if frames_to_remove:
            self.base = max(frames_to_remove) + 1
            print(f"🔄 Sender: Window moved, new base: {self.base % self.max_seq_num}")
    
    def is_in_range(self, seq_num: int, start: int, end: int) -> bool:
        """Check if sequence number is in range [start, end]"""
        if start <= end:
            return start <= seq_num <= end
        else:  # Wrap around case
            return seq_num >= start or seq_num <= end
    
    def check_timeouts(self, receiver):
        """Check for timeouts and retransmit if necessary"""
        current_time = time.time()
        oldest_unacked = min(self.window.keys()) if self.window else None
        
        if (oldest_unacked is not None and 
            current_time - self.window[oldest_unacked]['timestamp'] > self.timeout):
            
            print(f"⏰ Sender: Timeout detected for frame {oldest_unacked % self.max_seq_num}")
            self.go_back_n_retransmit(receiver, oldest_unacked)
    
    def go_back_n_retransmit(self, receiver, failed_seq_num: int):
        """Retransmit from failed frame onwards (Go-Back-N behavior)"""
        print(f"🔄 Sender: Go-Back-N retransmission starting from frame {failed_seq_num % self.max_seq_num}")
        
        # Check if we've exceeded retransmission limit
        if self.total_retransmission_count >= self.max_retransmissions:
            print(f"🚫 Sender: Maximum retransmissions ({self.max_retransmissions}) reached, stopping")
            return
        
        # Get all frames to retransmit (from failed frame onwards)
        frames_to_retransmit = []
        for seq_num in sorted(self.window.keys()):
            if seq_num >= failed_seq_num:
                frames_to_retransmit.append(seq_num)
        
        # Limit the number of frames to retransmit to prevent excessive load
        frames_to_retransmit = frames_to_retransmit[:self.window_size]
        
        # Retransmit frames
        for seq_num in frames_to_retransmit:
            if seq_num not in self.window:  # Check if frame still exists
                continue
                
            frame_info = self.window[seq_num]
            frame = frame_info['frame']
            
            print(f"📡 Sender: Retransmitting frame {frame.seq_num} with data '{frame.data}'")
            self.total_transmissions += 1
            self.retransmissions += 1
            self.total_retransmission_count += 1
            
            # Check retransmission limit during the loop
            if self.total_retransmission_count >= self.max_retransmissions:
                print(f"🚫 Sender: Retransmission limit reached during Go-Back-N")
                break
            
            # Update timestamp
            self.window[seq_num]['timestamp'] = time.time()
            
            # Send to receiver
            ack_num = receiver.receive_frame(frame)
            if ack_num is not None:
                self.process_ack(ack_num)
            
            time.sleep(0.1)
    
    def get_statistics(self):
        return {
            "total_transmissions": self.total_transmissions,
            "retransmissions": self.retransmissions,
            "efficiency": f"{((self.total_transmissions - self.retransmissions) / self.total_transmissions * 100):.1f}%" if self.total_transmissions > 0 else "0%"
        }

class GoBackNReceiver:
    def __init__(self):
        self.expected_seq_num = 0
        self.max_seq_num = 8
        self.received_frames = []
        self.total_frames_received = 0
        self.frames_discarded = 0
        
    def receive_frame(self, frame: Frame) -> Optional[int]:
        """Receive and process a frame"""
        self.total_frames_received += 1
        print(f"📥 Receiver: Received frame {frame.seq_num}")
        
        # Simulate frame loss during transmission
        if random.random() < 0.15:  # 15% frame loss rate
            print(f"📦 Receiver: Frame {frame.seq_num} lost during transmission")
            return None
        
        # Check for corruption
        if frame.is_corrupted():
            print(f"💥 Receiver: Frame {frame.seq_num} is corrupted")
            self.frames_discarded += 1
            return None
        
        # Check if this is the expected frame
        if frame.seq_num == self.expected_seq_num % self.max_seq_num:
            print(f"✅ Receiver: Frame {frame.seq_num} accepted - Data: '{frame.data}'")
            self.received_frames.append(frame.data)
            self.expected_seq_num += 1
            
            # Send ACK
            ack_num = frame.seq_num
            if self.send_ack(ack_num):
                return ack_num
        else:
            print(f"❌ Receiver: Frame {frame.seq_num} out of order (expected {self.expected_seq_num % self.max_seq_num}), discarded")
            self.frames_discarded += 1
            
            # Send ACK for the last correctly received frame
            if self.expected_seq_num > 0:
                last_correct_frame = (self.expected_seq_num - 1) % self.max_seq_num
                if self.send_ack(last_correct_frame):
                    return last_correct_frame
        
        return None
    
    def send_ack(self, seq_num: int) -> bool:
        """Send acknowledgment"""
        # Simulate ACK loss
        if random.random() < 0.1:  # 10% ACK loss rate
            print(f"📤 Receiver: ACK for frame {seq_num} sent but lost")
            return False
        print(f"📤 Receiver: ACK sent for frame {seq_num}")
        return True
    
    def get_received_data(self):
        return self.received_frames
    
    def get_statistics(self):
        return {
            "frames_received": self.total_frames_received,
            "frames_discarded": self.frames_discarded,
            "frames_accepted": len(self.received_frames)
        }

def demonstrate_go_back_n():
    """Demonstrate Go-Back-N ARQ protocol"""
    print("=" * 60)
    print("GO-BACK-N ARQ PROTOCOL SIMULATION")
    print("=" * 60)
    
    window_size = 4
    sender = GoBackNSender(window_size=window_size, timeout=1.5)
    receiver = GoBackNReceiver()
    
    # Test data to send
    test_data = ["Frame1", "Frame2", "Frame3", "Frame4", "Frame5", 
                "Frame6", "Frame7", "Frame8", "Frame9", "Frame10"]
    
    print(f"📋 Sending {len(test_data)} frames with window size {window_size}")
    
    sender.add_data(test_data)
    
    start_time = time.time()
    sender.send_frames(receiver)
    end_time = time.time()
    
    # Display results
    print("\n" + "=" * 60)
    print("SIMULATION RESULTS")
    print("=" * 60)
    
    sender_stats = sender.get_statistics()
    receiver_stats = receiver.get_statistics()
    
    print(f"📊 Frames to send: {len(test_data)}")
    print(f"📊 Frames accepted by receiver: {receiver_stats['frames_accepted']}")
    print(f"📊 Frames discarded by receiver: {receiver_stats['frames_discarded']}")
    print(f"📊 Total transmission attempts: {sender_stats['total_transmissions']}")
    print(f"📊 Retransmissions: {sender_stats['retransmissions']}")
    print(f"📊 Protocol efficiency: {sender_stats['efficiency']}")
    print(f"📊 Total simulation time: {end_time - start_time:.2f} seconds")
    print(f"📊 Received data: {receiver.get_received_data()}")
    
    # Protocol characteristics
    print(f"\n📚 Go-Back-N Characteristics:")
    print(f"   • Window size: {window_size} frames")
    print(f"   • Sequence number space: 0-{receiver.max_seq_num-1}")
    print(f"   • Sender can send multiple frames before getting ACK")
    print(f"   • On error: retransmit from error point onwards")
    print(f"   • Receiver accepts frames only in order")
    print(f"   • More efficient than Stop-and-Wait for good channels")

if __name__ == "__main__":
    # Set random seed for reproducible results (optional)
    random.seed(42)
    demonstrate_go_back_n()
