"""
Stop-and-Wait ARQ Protocol Simulation
=====================================
In this protocol:
- Sender sends one frame at a time
- Waits for ACK before sending next frame
- If no ACK received within timeout, retransmits the frame
- Simple but inefficient due to waiting time
"""

import time
import random
import threading
from dataclasses import dataclass
from typing import Optional
from enum import Enum

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

class StopAndWaitSender:
    def __init__(self, timeout: float = 2.0):
        self.timeout = timeout
        self.seq_num = 0
        self.waiting_for_ack = False
        self.current_frame: Optional[Frame] = None
        self.retransmission_count = 0
        self.total_transmissions = 0
        
    def send_frame(self, data: str, receiver) -> bool:
        """Send a frame using Stop-and-Wait protocol"""
        frame = Frame(self.seq_num, FrameType.DATA, data)
        self.current_frame = frame
        self.waiting_for_ack = True
        self.retransmission_count = 0
        
        print(f"\n📤 Sender: Preparing to send frame {frame.seq_num} with data: '{data}'")
        
        while self.waiting_for_ack and self.retransmission_count < 5:  # Max 5 retransmissions
            print(f"📡 Sender: Transmitting frame {frame.seq_num} (Attempt {self.retransmission_count + 1})")
            self.total_transmissions += 1
            
            # Simulate transmission delay
            time.sleep(0.1)
            
            # Send frame to receiver
            ack_received = receiver.receive_frame(frame)
            
            if ack_received:
                print(f"✅ Sender: ACK received for frame {frame.seq_num}")
                self.waiting_for_ack = False
                self.seq_num = 1 - self.seq_num  # Toggle between 0 and 1
                return True
            else:
                print(f"⏰ Sender: Timeout! No ACK received for frame {frame.seq_num}")
                self.retransmission_count += 1
                time.sleep(self.timeout)  # Wait before retransmission
        
        print(f"❌ Sender: Failed to send frame {frame.seq_num} after {self.retransmission_count} attempts")
        return False
    
    def get_statistics(self):
        return {
            "total_transmissions": self.total_transmissions,
            "efficiency": f"{(1/self.total_transmissions)*100:.1f}%" if self.total_transmissions > 0 else "0%"
        }

class StopAndWaitReceiver:
    def __init__(self):
        self.expected_seq_num = 0
        self.received_frames = []
        
    def receive_frame(self, frame: Frame) -> bool:
        """Receive and process a frame"""
        print(f"📥 Receiver: Received frame {frame.seq_num}")
        
        # Simulate frame loss during transmission
        if random.random() < 0.2:  # 20% frame loss rate
            print(f"📦 Receiver: Frame {frame.seq_num} lost during transmission")
            return False
        
        # Check for corruption
        if frame.is_corrupted():
            print(f"💥 Receiver: Frame {frame.seq_num} is corrupted")
            self.send_nak(frame.seq_num)
            return False
        
        # Check sequence number
        if frame.seq_num == self.expected_seq_num:
            print(f"✅ Receiver: Frame {frame.seq_num} accepted - Data: '{frame.data}'")
            self.received_frames.append(frame.data)
            self.expected_seq_num = 1 - self.expected_seq_num  # Toggle between 0 and 1
            self.send_ack(frame.seq_num)
            return True
        else:
            print(f"🔄 Receiver: Duplicate frame {frame.seq_num} discarded")
            self.send_ack(1 - self.expected_seq_num)  # Send ACK for previous frame
            return True  # Still send ACK to avoid infinite retransmission
    
    def send_ack(self, seq_num: int):
        """Send acknowledgment"""
        # Simulate ACK loss
        if random.random() < 0.1:  # 10% ACK loss rate
            print(f"📤 Receiver: ACK for frame {seq_num} sent but lost")
            return False
        print(f"📤 Receiver: ACK sent for frame {seq_num}")
        return True
    
    def send_nak(self, seq_num: int):
        """Send negative acknowledgment"""
        print(f"📤 Receiver: NAK sent for frame {seq_num}")
    
    def get_received_data(self):
        return self.received_frames

def demonstrate_stop_and_wait():
    """Demonstrate Stop-and-Wait ARQ protocol"""
    print("=" * 60)
    print("STOP-AND-WAIT ARQ PROTOCOL SIMULATION")
    print("=" * 60)
    
    sender = StopAndWaitSender(timeout=1.0)
    receiver = StopAndWaitReceiver()
    
    # Test data to send
    test_data = ["Hello", "World", "Stop", "And", "Wait", "Protocol"]
    
    print(f"📋 Sending {len(test_data)} frames...")
    
    successful_transmissions = 0
    start_time = time.time()
    
    for i, data in enumerate(test_data, 1):
        print(f"\n--- Sending Frame {i}/{len(test_data)} ---")
        if sender.send_frame(data, receiver):
            successful_transmissions += 1
        time.sleep(0.5)  # Small delay between frames
    
    end_time = time.time()
    
    # Display results
    print("\n" + "=" * 60)
    print("SIMULATION RESULTS")
    print("=" * 60)
    print(f"📊 Frames sent successfully: {successful_transmissions}/{len(test_data)}")
    print(f"📊 Total transmission attempts: {sender.get_statistics()['total_transmissions']}")
    print(f"📊 Protocol efficiency: {sender.get_statistics()['efficiency']}")
    print(f"📊 Total simulation time: {end_time - start_time:.2f} seconds")
    print(f"📊 Received data: {receiver.get_received_data()}")
    
    # Protocol characteristics
    print(f"\n📚 Stop-and-Wait Characteristics:")
    print(f"   • Window size: 1 frame")
    print(f"   • Sequence numbers: 0, 1 (alternating)")
    print(f"   • Sender waits for ACK before sending next frame")
    print(f"   • Simple but inefficient due to waiting time")
    print(f"   • Suitable for error-prone channels with low bandwidth")

if __name__ == "__main__":
    # Set random seed for reproducible results (optional)
    random.seed(42)
    demonstrate_stop_and_wait()
