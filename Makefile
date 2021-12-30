

APP = alexa_tv_control.py
SERVICE = alexa_tv_control

.PHONY: install
install: $(APP)
	# Install executable
	install -d -o root -g root -m 0755 $(DESTDIR)/usr/bin
	install -o root -g root -m 0755 $(APP) $(DESTDIR)/usr/bin
	# Install systemd service
	install -d -o root -g root -m 0755 $(DESTDIR)/lib/systemd/system
	install -o root -g root -m 0644 $(SERVICE).service $(DESTDIR)/lib/systemd/system
	systemctl enable $(SERVICE)


# Implicit rule to generate a C source file's dependencies.
%.d: %.cpp
	@echo DEPEND $<; \
	rm -f $@; \
	$(CXX) -MM $(CPPFLAGS) $(CXXFLAGS) $< > $@.$$$$; \
	sed 's,\($*\)\.o[ :]*,\1.o $@ : ,g' < $@.$$$$ > $@; \
	rm -f $@.$$$$

ifneq ($(MAKECMDGOALS), clean)
-include $(APP_OBJS:.o=.d)
endif
