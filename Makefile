TARGET=dist/RegisterCalculator

all: $(TARGET)

$(TARGET): src/run_calculator.py
	pyinstaller -y --onefile --noconsole --name $(notdir $(TARGET)) $<

clean:
	rm $(TARGET)
