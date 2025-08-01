# ARQ Protocols Simulation Project

This project implements and demonstrates three important Automatic Repeat Request (ARQ) protocols used in computer networks for reliable data transmission:

1. **Stop-and-Wait ARQ**
2. **Go-Back-N ARQ**  
3. **Selective Repeat ARQ**

## 🎯 Objectives

- Understand the working principles of different ARQ protocols
- Simulate basic flow control and error handling mechanisms
- Compare the efficiency and behavior of each protocol
- Demonstrate how each protocol handles packet loss, corruption, and acknowledgment issues

## 📁 Project Structure

```
Cn Continious Assessment 4/
├── arq_protocols_demo.py    # Main demonstration and comparison
├── stop_and_wait.py         # Stop-and-Wait ARQ implementation
├── go_back_n.py            # Go-Back-N ARQ implementation
├── selective_repeat.py     # Selective Repeat ARQ implementation
└── README.md               # This file
```

## 🚀 How to Run

### Prerequisites
- Python 3.7 or higher
- No external dependencies required (uses only standard library)

### Running Individual Protocols

```bash
# Run Stop-and-Wait simulation
python stop_and_wait.py

# Run Go-Back-N simulation
python go_back_n.py

# Run Selective Repeat simulation
python selective_repeat.py
```

### Running Complete Demonstration

```bash
# Run the main demo with menu options
python arq_protocols_demo.py
```

## 📋 Protocol Details

### 1. Stop-and-Wait ARQ

**Characteristics:**
- Sends one frame at a time
- Waits for ACK before sending next frame
- Simple but inefficient due to waiting time
- Sequence numbers: 0, 1 (alternating)

**Key Features:**
- Timeout and retransmission
- Duplicate detection
- Simple implementation

### 2. Go-Back-N ARQ

**Characteristics:**
- Sender can send N frames before needing ACK
- Uses sliding window protocol
- On error: retransmits from error point onwards
- Receiver accepts frames only in order

**Key Features:**
- Window size: N frames
- Cumulative acknowledgments
- Discards out-of-order frames
- More efficient than Stop-and-Wait

### 3. Selective Repeat ARQ

**Characteristics:**
- Sender sends multiple frames within window
- Individual acknowledgments for each frame
- Retransmits only lost/corrupted frames
- Buffers out-of-order frames at receiver

**Key Features:**
- Most efficient protocol
- Individual frame timers
- Complex buffer management
- Selective retransmission

## 🧪 Simulation Features

### Error Simulation
- **Frame Loss**: 15% probability during transmission
- **Frame Corruption**: 10% probability 
- **ACK Loss**: 10% probability
- **Timeout Handling**: Configurable timeout periods

### Statistics Tracking
- Total transmissions
- Retransmissions count
- Protocol efficiency
- Transmission time
- Success rate

### Visual Output
- Frame-by-frame transmission logs
- ACK/NAK messages
- Error notifications
- Performance statistics
- Protocol comparison results

## 📊 Example Output

```
📤 Sender: Transmitting frame 0 (Attempt 1)
📥 Receiver: Received frame 0
✅ Receiver: Frame 0 accepted - Data: 'Hello'
📤 Receiver: ACK sent for frame 0
✅ Sender: ACK received for frame 0

📊 Protocol efficiency: 85.7%
📊 Total transmission attempts: 14
📊 Retransmissions: 2
```

## 🔬 Educational Value

This simulation helps understand:

1. **Flow Control**: How protocols manage data flow between sender and receiver
2. **Error Detection**: Checksum-based corruption detection
3. **Error Recovery**: Different retransmission strategies
4. **Protocol Efficiency**: Trade-offs between simplicity and performance
5. **Network Reliability**: How protocols ensure reliable data delivery

## 🎛️ Customization

You can modify simulation parameters:

```python
# In the protocol files, adjust:
timeout = 2.0           # Timeout duration
window_size = 4         # Window size for windowed protocols
corruption_rate = 0.1   # Frame corruption probability
loss_rate = 0.15        # Frame loss probability
ack_loss_rate = 0.1     # ACK loss probability
```

## 📈 Performance Comparison

| Protocol | Window Size | Complexity | Efficiency | Best Use Case |
|----------|------------|------------|------------|---------------|
| Stop-and-Wait | 1 | Simple | Low | Noisy channels |
| Go-Back-N | N | Medium | Medium | Good channels |
| Selective Repeat | N (both ends) | Complex | High | High-speed links |

## 🏆 Learning Outcomes

After running these simulations, you will understand:

- How different ARQ protocols handle reliability
- The trade-offs between simplicity and efficiency
- Why protocol choice depends on network conditions
- How windowing improves protocol performance
- The importance of proper timeout values
- Buffer management in networking protocols

## 🛠️ Technical Implementation

### Key Classes
- `Frame`: Represents data/control frames
- `Sender`: Implements transmission logic
- `Receiver`: Implements reception and acknowledgment logic

### Key Methods
- `send_frame()`: Frame transmission with timeout
- `receive_frame()`: Frame reception and processing
- `process_ack()`: Acknowledgment handling
- `check_timeouts()`: Timeout detection and retransmission

## 🎯 Assignment Objectives Met

✅ Simulate Stop-and-Wait ARQ Protocol  
✅ Implement sender that sends frames one at a time  
✅ Receiver sends ACK if frame received correctly  
✅ Timeout and retransmission logic  

✅ Simulate Go-Back-N ARQ  
✅ Sender can send N frames before needing ACK  
✅ Retransmit from error point onwards  
✅ Implement sender & receiver buffer logic  

✅ Simulate Selective Repeat ARQ  
✅ Sender sends multiple frames  
✅ Individual acknowledgments  
✅ Selective retransmission of lost frames  
✅ Out-of-order frame buffering  

## 📚 Further Reading

- Computer Networks by Andrew Tanenbaum
- Data Communications and Networking by Behrouz Forouzan
- RFC 1122 - Requirements for Internet Hosts
- TCP/IP Illustrated by W. Richard Stevens


