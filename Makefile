TARGET=dist/RegisterCalculator

all: $(TARGET)

$(TARGET): src/run_calculator.py
	pyinstaller -y --noconsole --collect-all tkinterdnd2 --name $(notdir $(TARGET)) $<

clean:
	rm $(TARGET)
