# udpsocket
 This test program use python to send udp message and recv message.
 
 before I send message, I must send 'session start' message to server. and after I deal with message, I need to send 'session end' message. So I use Decorator.

# Prerequisites:
both python2 and python3 are ok.

# Run
git clone https://github.com/cynthia1wang/udpsocket.git

$python server.py

$python client.py

# Result
server：

recv =  b'7e8e000001000d73657373696f6e2073746172747e'

recv =  b'7e8e080003000a686561727420626561747e'

recv =  b'7e8e0a0005000b73657373696f6e20656e647e'

client:

send session start

recv =  b'7e8e010002000d73657373696f6e5f7374617274007e'

send heart beat

recv =  b'7e8e090004000b73657373696f6e5f656e007e'

send session end

recv =  b'7e8e0b0006000b73657373696f6e5f656e64007e'
