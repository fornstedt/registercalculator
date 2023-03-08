TARGET=reg_calc
TARGET_EXE=dist/$(TARGET).exe

all: $(TARGET_EXE)

$(TARGET_EXE): $(TARGET).py
	pyinstaller --onefile --noconsole $<

clean:
	rm $(TARGET_EXE)
