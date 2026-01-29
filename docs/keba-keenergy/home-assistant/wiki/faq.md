# FAQ - Troubleshooting

**Q**: I can't connect to the KEBA KeEnergy device and get "Failed to connect".

**A**: Always enter the IP or hostname without the port or protocol! Correct: `10.10.0.1` Incorrect: `10.10.0.1:443`
or `https://ap4040.local`

---

**Q**: Is it possible to create automations that change the parameters on the controller?

**A**: The built-in flash memory (NAND) has a limited lifespan. Excessive writing that deviates from normal user
habits should be avoided. [(Issue #23)](https://github.com/superbox-dev/keba_keenergy/issues/23)
