TARGET=reg_calc
TARGET_EXE=dist/$(TARGET).exe

all: $(TARGET_EXE)

$(TARGET_EXE): $(TARGET).py
	pyinstaller -y --onefile --noconsole $<
	pyinstaller -y --noconsole $<

clean:
	rm $(TARGET_EXE)
