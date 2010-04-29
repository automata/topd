import oscP5.*;
import netP5.*;

NetAddress toPD;

void setup() {
  size(400,400);
  frameRate(25);
  toPD = new NetAddress("127.0.0.1",12000);
}

void draw() {
  background(0);
}


void mousePressed() {
  OscMessage myOscMessage = new OscMessage("/obj");
  
  myOscMessage.add("osc~ 440");
  myOscMessage.add(100);
  myOscMessage.add(200);
  
  OscP5.flush(myOscMessage, toPD);
}
