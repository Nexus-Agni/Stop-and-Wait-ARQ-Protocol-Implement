"""
Selective Repeat ARQ Protocol Simulation
=======================================
In this protocol:
- Sender sends multiple frames within a window
- Receiver acknowledges frames individually and buffers out-of-order frames
- Sender retransmits only the erroneous/lost frames (selective retransmission)
- Most efficient but requires more complex buffer management
"""

import time
import random
import threading
from dataclasses import dataclass
from typing import List, Optional, Dict
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

class SelectiveRepeatSender:
    def __init__(self, window_size: int = 4, timeout: float = 2.0):
        self.window_size = window_size
        self.timeout = timeout
        self.base = 0  # Base of the window
        self.next_seq_num = 0  # Next sequence number to use
        self.window = {}  # Sent but not acknowledged frames
        self.ack_received = set()  # Set of acknowledged sequence numbers
        self.data_buffer = deque()  # Buffer for data to send
        self.max_seq_num = 8  # Sequence number space (0-7)
        self.total_transmissions = 0
        self.retransmissions = 0
        self.individual_timers = {}  # Individual timers for each frame
        
    def add_data(self, data_list: List[str]):
        """Add data to the buffer for transmission"""
        self.data_buffer.extend(data_list)
        print(f"📋 Sender: Added {len(data_list)} frames to buffer")
    
    def can_send(self) -> bool:
        """Check if we can send more frames"""
        return (self.next_seq_num < self.base + self.window_size and 
                len(self.data_buffer) > 0)
    
    def send_frames(self, receiver) -> bool:
        """Send frames using Selective Repeat protocol"""
        print(f"\n📤 Sender: Starting transmission with window size {self.window_size}")
        
        while self.data_buffer or self.window:
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
                
                # Start individual timer for this frame
                self.individual_timers[self.next_seq_num] = time.time()
                
                self.total_transmissions += 1
                
                # Send to receiver
                ack_nums = receiver.receive_frame(frame)
                
                if ack_nums:
                    for ack_num in ack_nums:
                        self.process_ack(ack_num)
                
                self.next_seq_num += 1
                time.sleep(0.1)  # Small delay between transmissions
            
            # Check for individual frame timeouts
            self.check_individual_timeouts(receiver)
            
            # Try to slide the window
            self.slide_window()
            
            # If no frames in window and no data to send, we're done
            if not self.window and not self.data_buffer:
                break
                
            time.sleep(0.1)
        
        print(f"✅ Sender: All frames transmitted successfully")
        return True
    
    def process_ack(self, ack_num: int):
        """Process received ACK for individual frame"""
        print(f"✅ Sender: Received ACK for frame {ack_num}")
        
        # Mark frame as acknowledged
        self.ack_received.add(ack_num)
        
        # Remove from window if present
        seq_nums_to_remove = [seq_num for seq_num in self.window.keys() 
                             if seq_num % self.max_seq_num == ack_num]
        
        for seq_num in seq_nums_to_remove:
            if seq_num in self.window:
                del self.window[seq_num]
            if seq_num in self.individual_timers:
                del self.individual_timers[seq_num]
    
    def slide_window(self):
        """Slide the window forward if possible"""
        original_base = self.base
        
        # Advance base to the first unacknowledged frame
        while self.base % self.max_seq_num in self.ack_received:
            self.ack_received.remove(self.base % self.max_seq_num)
            self.base += 1
        
        if self.base != original_base:
            print(f"🔄 Sender: Window slid forward, new base: {self.base % self.max_seq_num}")
    
    def check_individual_timeouts(self, receiver):
        """Check for individual frame timeouts and retransmit only those frames"""
        current_time = time.time()
        frames_to_retransmit = []
        
        for seq_num, timestamp in list(self.individual_timers.items()):
            if current_time - timestamp > self.timeout:
                frames_to_retransmit.append(seq_num)
        
        # Retransmit timed-out frames
        for seq_num in frames_to_retransmit:
            if seq_num in self.window:
                self.selective_retransmit(receiver, seq_num)
    
    def selective_retransmit(self, receiver, seq_num: int):
        """Retransmit only the specific frame (Selective Repeat behavior)"""
        if seq_num not in self.window:  # Check if frame still exists
            return
            
        frame_info = self.window[seq_num]
        frame = frame_info['frame']
        
        print(f"🔄 Sender: Selective retransmission of frame {frame.seq_num} with data '{frame.data}'")
        self.total_transmissions += 1
        self.retransmissions += 1
        
        # Update timestamp and timer
        self.window[seq_num]['timestamp'] = time.time()
        self.individual_timers[seq_num] = time.time()
        
        # Send to receiver
        ack_nums = receiver.receive_frame(frame)
        if ack_nums:
            for ack_num in ack_nums:
                self.process_ack(ack_num)
        
        time.sleep(0.1)
    
    def get_statistics(self):
        return {
            "total_transmissions": self.total_transmissions,
            "retransmissions": self.retransmissions,
            "efficiency": f"{((self.total_transmissions - self.retransmissions) / self.total_transmissions * 100):.1f}%" if self.total_transmissions > 0 else "0%"
        }

class SelectiveRepeatReceiver:
    def __init__(self, window_size: int = 4):
        self.window_size = window_size
        self.base = 0  # Base of receiver window
        self.max_seq_num = 8
        self.buffer = {}  # Buffer for out-of-order frames
        self.received_frames = []  # Final ordered sequence
        self.total_frames_received = 0
        self.frames_discarded = 0
        self.duplicate_frames = 0
        
    def receive_frame(self, frame: Frame) -> Optional[List[int]]:
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
        
        # Check if frame is within receiver window
        if self.is_in_window(frame.seq_num):
            if frame.seq_num in self.buffer:
                print(f"🔄 Receiver: Duplicate frame {frame.seq_num}, sending ACK")
                self.duplicate_frames += 1
            else:
                print(f"✅ Receiver: Frame {frame.seq_num} buffered - Data: '{frame.data}'")
                self.buffer[frame.seq_num] = frame.data
            
            # Send ACK for this specific frame
            ack_nums = []
            if self.send_ack(frame.seq_num):
                ack_nums.append(frame.seq_num)
            
            # Try to deliver frames in order
            delivered_frames = self.deliver_frames()
            return ack_nums + delivered_frames
        else:
            # Frame outside window
            if self.is_already_delivered(frame.seq_num):
                print(f"🔄 Receiver: Already delivered frame {frame.seq_num}, sending ACK")
                # Send ACK for already delivered frame
                if self.send_ack(frame.seq_num):
                    return [frame.seq_num]
            else:
                print(f"❌ Receiver: Frame {frame.seq_num} outside window [{self.base % self.max_seq_num}-{(self.base + self.window_size - 1) % self.max_seq_num}], discarded")
                self.frames_discarded += 1
        
        return None
    
    def is_in_window(self, seq_num: int) -> bool:
        """Check if sequence number is within receiver window"""
        window_end = (self.base + self.window_size - 1) % self.max_seq_num
        
        if self.base % self.max_seq_num <= window_end:
            return self.base % self.max_seq_num <= seq_num <= window_end
        else:  # Window wraps around
            return seq_num >= self.base % self.max_seq_num or seq_num <= window_end
    
    def is_already_delivered(self, seq_num: int) -> bool:
        """Check if frame was already delivered"""
        return seq_num < self.base % self.max_seq_num
    
    def deliver_frames(self) -> List[int]:
        """Deliver frames in order and slide window"""
        delivered_acks = []
        
        # Deliver consecutive frames starting from base
        while self.base % self.max_seq_num in self.buffer:
            seq_num = self.base % self.max_seq_num
            data = self.buffer[seq_num]
            self.received_frames.append(data)
            del self.buffer[seq_num]
            
            print(f"📤 Receiver: Delivered frame {seq_num} to upper layer - Data: '{data}'")
            self.base += 1
        
        if delivered_acks:
            print(f"🔄 Receiver: Window slid to base {self.base % self.max_seq_num}")
        
        return delivered_acks
    
    def send_ack(self, seq_num: int) -> bool:
        """Send acknowledgment for specific frame"""
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
            "duplicate_frames": self.duplicate_frames,
            "frames_delivered": len(self.received_frames),
            "frames_buffered": len(self.buffer)
        }

def demonstrate_selective_repeat():
    """Demonstrate Selective Repeat ARQ protocol"""
    print("=" * 60)
    print("SELECTIVE REPEAT ARQ PROTOCOL SIMULATION")
    print("=" * 60)
    
    window_size = 4
    sender = SelectiveRepeatSender(window_size=window_size, timeout=1.5)
    receiver = SelectiveRepeatReceiver(window_size=window_size)
    
    # Test data to send
    test_data = ["Alpha", "Beta", "Gamma", "Delta", "Epsilon", 
                "Zeta", "Eta", "Theta", "Iota", "Kappa"]
    
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
    print(f"📊 Frames delivered by receiver: {receiver_stats['frames_delivered']}")
    print(f"📊 Frames currently buffered: {receiver_stats['frames_buffered']}")
    print(f"📊 Frames discarded: {receiver_stats['frames_discarded']}")
    print(f"📊 Duplicate frames received: {receiver_stats['duplicate_frames']}")
    print(f"📊 Total transmission attempts: {sender_stats['total_transmissions']}")
    print(f"📊 Retransmissions: {sender_stats['retransmissions']}")
    print(f"📊 Protocol efficiency: {sender_stats['efficiency']}")
    print(f"📊 Total simulation time: {end_time - start_time:.2f} seconds")
    print(f"📊 Received data: {receiver.get_received_data()}")
    
    # Protocol characteristics
    print(f"\n📚 Selective Repeat Characteristics:")
    print(f"   • Sender window size: {window_size} frames")
    print(f"   • Receiver window size: {window_size} frames")
    print(f"   • Sequence number space: 0-{receiver.max_seq_num-1}")
    print(f"   • Individual ACKs for each frame")
    print(f"   • Selective retransmission of lost/corrupted frames only")
    print(f"   • Out-of-order frame buffering at receiver")
    print(f"   • Most efficient but complex implementation")

if __name__ == "__main__":
    # Set random seed for reproducible results (optional)
    random.seed(42)
    demonstrate_selective_repeat()
