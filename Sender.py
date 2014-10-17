import sys
import getopt

import Checksum
import BasicSender

'''
This is a skeleton sender class. Create a fantastic transport protocol here.
'''
class Sender(BasicSender.BasicSender):
    def __init__(self, dest, port, filename, debug=False, sackMode=False):
        super(Sender, self).__init__(dest, port, filename, debug)
        if sackMode:
            raise NotImplementedError #remove this line when you implement SACK
        self.RETRANSMIT_TIME = 500;
        self.WINDOW_SIZE = 5;
        self.inflight = []
        self.inflight_seqno = []

    # Main sending loop.
    def start(self):
        seqno = 0
        # Note: this reads in 1400 characters at a time, which equals 1400 bytes.
        msgs = self.splitInput()
        #msg = self.infile.read(1400)
        msg_type = None
        while (not (msg_type == 'end' and len(self.inflight) == 0)):
            while (len(self.inflight) < self.WINDOW_SIZE and len(msgs) > 0):
                next_msg = msgs.pop(0)
                msg_type = 'data'
                if seqno == 0:
                    msg_type = 'start'
                elif (next_msg == ""):
                    msg_type = 'end'
                    break
                packet = self.make_packet(msg_type,seqno,next_msg)
                self.inflight.append(packet)
                self.inflight_seqno.append(seqno)
                self.send(packet)
                seqno += 1
                print "sent: %s" % packet
            response = self.receive(self.RETRANSMIT_TIME)
            if (response != None):
                self.handle_response(response)
            else:
                self.handle_timeout()
        self.infile.close()

    # Splits input into 1400 byte strings.
    def splitInput(self):
        messages = []
        msg = self.infile.read(1400)
        messages.append(msg)
        while msg != "":
            msg = self.infile.read(1400)
            messages.append(msg)
        return messages

    # Handles a response from the receiver.
    def handle_response(self,response_packet):
        if Checksum.validate_checksum(response_packet):
            print "recv: %s" % response_packet
            msg_type, seqno, data, checksum = self.split_packet(response_packet)
            if ((int(seqno) - 1) == self.inflight_seqno[0]):
                self.inflight_seqno.pop(0)
                self.inflight.pop(0)
            else:
                #Need to handle duplicate logic here.

        else:
            print "recv: %s <--- CHECKSUM FAILED" % response_packet
        # Need to extend this to include reliability

    # Handles timeouts that occur
    def handle_timeout(self):
        pass

    # Handles acks sent from receiver.
    def handle_new_ack(self, ack):
        pass

    # Handles duplicate acks from receiver.
    def handle_dup_ack(self, ack):
        pass

    def log(self, msg):
        if self.debug:
            print msg


'''
This will be run if you run this script from the command line. You should not
change any of this; the grader may rely on the behavior here to test your
submission.
'''
if __name__ == "__main__":
    def usage():
        print "BEARS-TP Sender"
        print "-f FILE | --file=FILE The file to transfer; if empty reads from STDIN"
        print "-p PORT | --port=PORT The destination port, defaults to 33122"
        print "-a ADDRESS | --address=ADDRESS The receiver address or hostname, defaults to localhost"
        print "-d | --debug Print debug messages"
        print "-h | --help Print this usage message"
        print "-k | --sack Enable selective acknowledgement mode"

    try:
        opts, args = getopt.getopt(sys.argv[1:],
                               "f:p:a:dk", ["file=", "port=", "address=", "debug=", "sack="])
    except:
        usage()
        exit()

    port = 33122
    dest = "localhost"
    filename = None
    debug = False
    sackMode = False

    for o,a in opts:
        if o in ("-f", "--file="):
            filename = a
        elif o in ("-p", "--port="):
            port = int(a)
        elif o in ("-a", "--address="):
            dest = a
        elif o in ("-d", "--debug="):
            debug = True
        elif o in ("-k", "--sack="):
            sackMode = True

    s = Sender(dest, port, filename, debug, sackMode)
    try:
        s.start()
    except (KeyboardInterrupt, SystemExit):
        exit()


###########################################################
#
# Create number of packets needed for WINDOW_SIZE instead of just 1
# Send Start with empty string
# Upon receiving start, send WINDOW_SIZE packets
# Wait until ack matches your sequence number
#     if you timeout, resend window starting at last acked packet.
# Otherwise, send next window of packets.
