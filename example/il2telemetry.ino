#include <U8g2lib.h>
#include <LiquidCrystal_I2C.h>

#ifdef U8X8_HAVE_HW_SPI
#include <SPI.h>
#endif
#ifdef U8X8_HAVE_HW_I2C
#include <Wire.h>
#endif

#define MAX_PARAM_LEN 20

U8G2_SSD1309_128X64_NONAME2_F_4W_HW_SPI u8g2(U8G2_R0, /* cs=*/ 5, /* dc=*/16, /* reset=*/ 17);  


void ScaleDraw(char indicated_str[10], int x_pos, int orientation=1, int step_size=1000);
void DrawTachometer(int x_pos, int y_pos, char indicated_rpm[10]);

const byte num_bytes = 100;
const byte packet_marker = 0x3A;
const byte seperator = 0x2C;
byte received_bytes[num_bytes];
boolean new_data = false;

int lcdColumns = 16;
int lcdRows = 2;

LiquidCrystal_I2C lcd(0x27, lcdColumns, lcdRows);

char lcd_test_text[20] = "Static Message";

struct Telemetry {
  char *active_param = NULL;
  void *active_param_update(void);
  char engine_rpm[MAX_PARAM_LEN];
  char engine_mp[MAX_PARAM_LEN];
  char altitude[MAX_PARAM_LEN] =  "0";
  char speed[MAX_PARAM_LEN];
  char heading[MAX_PARAM_LEN];
  char vertical_speed[MAX_PARAM_LEN];
  char slip[MAX_PARAM_LEN];
};

struct Telemetry telem;

void setup(void) {
	u8g2.begin();
  lcd.init();
  lcd.backlight();
    Serial.begin(115200);
    Serial.print(F("<Here we go!>"));

}

void loop() {
    lcd.setCursor(0,0);
    lcd.print(lcd_test_text);

    RecvBytes();
    if (new_data == true) {
        int i = 0;
        int param_pos = 0;
        int param_id = 0;

        while (received_bytes[i] != packet_marker) {
          switch (received_bytes[i]) {
            case 'A':
              if(telem.active_param) {
                telem.active_param[i-1] = '\0';
                param_pos = 0;
              }
              telem.active_param = telem.altitude;
              break;
            case 'S':
              if(telem.active_param) {
                telem.active_param[i-1] = '\0';
                param_pos = 0;
              }             
              telem.active_param = telem.speed;
              break;
            case 'V':
              if(telem.active_param) {
                telem.active_param[i-1] = '\0';
                param_pos = 0;
              }
              telem.active_param = telem.vertical_speed;
              break;
            case 'R':
              if(telem.active_param) {
                telem.active_param[param_pos-1] = '\0';
                param_pos = 0;
              }
              telem.active_param = telem.engine_rpm;
              break;
            case 'P':
              if(telem.active_param) {
                telem.active_param[param_pos-1] = '\0';
                param_pos = 0;
              }
              telem.active_param = telem.engine_mp;
              break;
            case 'H':
              if(telem.active_param) {
                telem.active_param[param_pos-1] = '\0';
                param_pos = 0;
              }
              telem.active_param = telem.heading;
              break;
            case 'B':
              if(telem.active_param) {
                telem.active_param[param_pos-1] = '\0';
                param_pos = 0;
              }
              telem.active_param = telem.slip;
              break;
            default:
              if(telem.active_param) {
                telem.active_param[param_pos-1] = received_bytes[i];
              }
              break;
          }
          if(!telem.active_param) {
            break;
          }
          i++;
          param_pos++;
        }

        if(telem.active_param) {
          telem.active_param[param_pos-1] = '\0';
        }

        new_data = false;
    }
    
    for(int i = 0 ; i < 30000; i=i+50) {
        char buffer[10];
        u8g2.clearBuffer();
        u8g2.setDrawColor(1);
        DrawTachometer(63, 30, itoa(i, buffer, 10));
        u8g2.setFont(u8g2_font_baby_tn);
        ScaleDraw(itoa(i, buffer, 10), 0);
        ScaleDraw(itoa((30000-i)/100, buffer, 10), 125, -1, 20);
        SlipIndicator();
        DrawHeading(41,7,"123");
        DrawManifold(79,7,"54");
        u8g2.sendBuffer();
        delay(100);
    }
}

void DrawHeading(int x_pos, int y_pos, char indicated_heading[5]) {
  u8g2.setFont(u8g2_font_blipfest_07_tn);
  u8g2.drawButtonUTF8(x_pos, y_pos, U8G2_BTN_BW1, 0, 1, 1, indicated_heading);
}

void DrawManifold(int x_pos, int y_pos, char indicated_press[10]) {
  u8g2.setFont(u8g2_font_blipfest_07_tn);
  u8g2.drawButtonUTF8(x_pos, y_pos, U8G2_BTN_BW1, 0, 1, 1, indicated_press);
}

void DrawTachometer(int x_pos, int y_pos, char indicated_rpm[10]) {
  int indicated = atoi(indicated_rpm);
  char first_digit[2] = "0";
  first_digit[0] = indicated_rpm[0];
  first_digit[1] = '\0';
  u8g2.setFont(u8g2_font_blipfest_07_tn);
  u8g2.drawCircle(x_pos, y_pos, 21);
  char reading_buffer[2];
  for(int i=0; i<10; i++) {
    u8g2.drawStr(x_pos -1  + 16*sin(i*2*PI/10), y_pos + 3 - 16*cos(i*2*PI/10), itoa(i,reading_buffer,10));
  }
  for(int k=1; k<20; k=k+2) {
    u8g2.drawLine(x_pos+17*sin(k*2*PI/20), y_pos-16*cos(k*2*PI/20), x_pos+21*sin(k*2*PI/20), y_pos-21*cos(k*2*PI/20));
  }
  float theta = (2*PI/1000) * (indicated%1000);
  u8g2.drawLine(x_pos, y_pos, x_pos + 12*sin(theta), y_pos - 12*cos(theta));
  u8g2.drawFrame(x_pos-24, y_pos+14, 7, 9);
  u8g2.drawStr(x_pos-22, y_pos+21, first_digit);
}

void ScaleDraw(char indicated_str[10], int x_pos, int orientation, int step_size) {
    u8g2.drawTriangle((orientation == -1 ? x_pos + 1 : x_pos), 27, (orientation == -1 ? x_pos-4 : x_pos+5), 30, (orientation == -1 ? x_pos + 1 : x_pos), 33);
    u8g2.drawLine(x_pos+(orientation*6), 0, x_pos+(orientation*6), 63);
    unsigned int indicated = atoi(indicated_str);
    unsigned int top_visible_read = (indicated - (indicated%step_size) + 2*step_size);
    int scale_offset = 10 - (indicated%step_size)/(step_size/20);
    char scale_buffer[10];
     for(int i=0; i <=63; i=i+2) {
        u8g2.drawLine(x_pos+(orientation*6), i+(abs(scale_offset)%2), x_pos+(orientation*8), i+(abs(scale_offset)%2));
        if(!(i%10)) {
            u8g2.drawLine(x_pos+(orientation*6), i-scale_offset, x_pos+(orientation*10), i-scale_offset);
        }
        if(!(i%20)) {
            u8g2.drawLine(x_pos+(orientation*6), i-scale_offset, x_pos+(orientation*12), i-scale_offset);
            itoa(top_visible_read-(i*(step_size/20)), scale_buffer, 10);
            int str_width = u8g2.getStrWidth(scale_buffer);
            u8g2.drawStr(x_pos+(orientation==-1 ? (-15-str_width) : 15), i-scale_offset+3, scale_buffer);
        }
    }
}

void SlipIndicator() {
  u8g2.drawLine(45,54,81,54);
  u8g2.drawPixel(43,54);
  u8g2.drawPixel(41,54);
  u8g2.drawPixel(39,54);
  u8g2.drawPixel(83,54);
  u8g2.drawPixel(85,54);
  u8g2.drawPixel(87,54);
  u8g2.drawLine(45,62,81,62);
  u8g2.drawPixel(43,62);
  u8g2.drawPixel(41,62);
  u8g2.drawPixel(39,62);
  u8g2.drawPixel(83,62);
  u8g2.drawPixel(85,62);
  u8g2.drawPixel(87,62);
  u8g2.drawFilledEllipse(63,58,3,4);
}

void RecvBytes() {
  static boolean recv_in_progress = false;
  static byte ndx = 0;
  byte rb = 0;
  while (Serial.available() > 0 && new_data == false) {
    rb = Serial.read();
    if (recv_in_progress == true) {
      received_bytes[ndx] = rb;
      ndx++;
      if (rb == packet_marker) {
          received_bytes[ndx] = '\0';
          recv_in_progress = false;
          new_data = true;
          ndx = 0;
      }
    }
    else if(rb == packet_marker) {
      recv_in_progress = true;    
    }
  }
}
