# see http://web.mit.edu/6.111/www/f2017/handouts/FFTtutorial121102.pdf

from nmigen import *
from nmigen.build import Platform
from nmigen.cli import main

class ClockDivider(Elaboratable):
    def __init__(self):
        self.clk = Signal()
        self.clk2 = Signal()
        self.clk4 = Signal()
        self.clk8 = Signal()

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        reg = Signal(3)

        m.d.sync += reg.eq(reg + 1)
        m.d.comb += self.clk2.eq(reg[0])
        m.d.comb += self.clk4.eq(reg[1])
        m.d.comb += self.clk8.eq(reg[2])

        return m

class Clock4Phase(Elaboratable):
    def __init__(self):
        self.clka = Signal()
        self.clkb = Signal()
        self.clkc = Signal()
        self.clkd = Signal()

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        reg = Signal(2)
        m.d.sync += reg.eq(reg + 1)
        m.d.comb += self.clka.eq(reg == 0)
        m.d.comb += self.clkb.eq(reg == 1)
        m.d.comb += self.clkc.eq(reg == 2)
        m.d.comb += self.clkd.eq(reg == 3)

        return m


class Butterfly(Elaboratable):
    def __init__(self):

        self.a_real = Signal(signed(21))
        self.a_imag = Signal(signed(21))
        self.b_real = Signal(signed(21))
        self.b_imag = Signal(signed(21))

        self.tw_real = Signal(signed(21))
        self.tw_imag = Signal(signed(21))

        self.a_prime_real = Signal(signed(21))
        self.a_prime_imag = Signal(signed(21))
        self.b_prime_real = Signal(signed(21))
        self.b_prime_imag = Signal(signed(21))

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        clk_phase = Clock4Phase()

        m.submodules += clk_phase

        sync1 = ClockDomain("sync1")
        sync2 = ClockDomain("sync2")
        sync3 = ClockDomain("sync3")
        sync4 = ClockDomain("sync4")

        a_tmp_real = Signal(signed(42))
        a_tmp_imag = Signal(signed(42))
        b_tmp_real = Signal(signed(42))
        b_tmp_imag = Signal(signed(42))

        # maybe this requires more intelligent clocking?
        # also I was tired when doing the bitshifts and they're probably wrong
        # should test complex multiplier
        m.d.sync += a_tmp_real.eq(self.a_real)
        m.d.sync += a_tmp_imag.eq(self.a_imag)
        m.d.sync += b_tmp_real.eq((self.b_real * self.tw_real) - (self.b_imag * self.tw_imag))
        m.d.sync += b_tmp_imag.eq((self.b_real * self.tw_imag) + (self.b_imag * self.tw_real))

        m.d.sync += self.a_prime_real.eq(a_tmp_real + b_tmp_real[20:41])
        m.d.sync += self.a_prime_imag.eq(a_tmp_imag + b_tmp_imag[20:41])
        m.d.sync += self.b_prime_real.eq(a_tmp_real - b_tmp_real[20:41])
        m.d.sync += self.b_prime_imag.eq(a_tmp_imag - b_tmp_imag[20:41])

        return m

if __name__ == "__main__":
    top = Butterfly()

    main(top, ports=(top.a_real,))
