# see http://web.mit.edu/6.111/www/f2017/handouts/FFTtutorial121102.pdf

from nmigen import *
from nmigen.build import Platform
from nmigen.cli import main

# class ClockDivider(Elaboratable):
#     def __init__(self):
#         self.clk = Signal()
#         self.clk2 = Signal()
#         self.clk4 = Signal()
#         self.clk8 = Signal()
#
#     def elaborate(self, platform: Platform) -> Module:
#         m = Module()
#
#         reg = Signal(3)
#
#         m.d.sync += reg.eq(reg + 1)
#         m.d.comb += self.clk2.eq(reg[0])
#         m.d.comb += self.clk4.eq(reg[1])
#         m.d.comb += self.clk8.eq(reg[2])
#
#         return m
#
# class Clock4Phase(Elaboratable):
#     def __init__(self):
#         self.clka = Signal()
#         self.clkb = Signal()
#         self.clkc = Signal()
#         self.clkd = Signal()
#
#     def elaborate(self, platform: Platform) -> Module:
#         m = Module()
#
#         reg = Signal(2)
#         m.d.sync += reg.eq(reg + 1)
#         m.d.comb += self.clka.eq(reg == 0)
#         m.d.comb += self.clkb.eq(reg == 1)
#         m.d.comb += self.clkc.eq(reg == 2)
#         m.d.comb += self.clkd.eq(reg == 3)
#
#         return m

class Butterfly(Elaboratable):
    def __init__(self):

        self.start = Signal()
        self.done = Signal()

        self.a_real = Signal(signed(21))
        self.a_imag = Signal(signed(21))
        self.b_real = Signal(signed(21))
        self.b_imag = Signal(signed(21))

        self.tw_real = Signal(signed(21))
        self.tw_imag = Signal(signed(21))

        self.b_tmp_real = Signal(signed(42))
        self.b_tmp_imag = Signal(signed(42))

        self.a_prime_real = Signal(signed(21))
        self.a_prime_imag = Signal(signed(21))
        self.b_prime_real = Signal(signed(21))
        self.b_prime_imag = Signal(signed(21))

    def ports(self):
        return [self.start, self.done,
                self.a_real, self.a_imag,
                self.b_real, self.b_imag,
                self.tw_real, self.tw_imag,
                self.a_prime_real, self.a_prime_imag,
                self.b_prime_real, self.b_prime_imag]

    def elaborate(self, platform: Platform) -> Module:
        m = Module()

        reg = Signal(4)

        syncn = ClockDomain("syncn", clk_edge="neg")
        sync1 = ClockDomain("sync1")
        sync2 = ClockDomain("sync2")
        sync3 = ClockDomain("sync3")

        clk1 = Signal()
        clk2 = Signal()
        clk3 = Signal()
        sync1.clk = clk1
        sync2.clk = clk2
        sync3.clk = clk3
        m.d.comb += clk1.eq(reg[0])
        m.d.comb += clk2.eq(reg[1])
        m.d.comb += clk3.eq(reg[2])

        # TODO: tie resets together?

        m.domains += [syncn, sync1, sync2, sync3]

        m.d.sync += reg.eq(reg << 1)
        m.d.sync += reg[0].eq(self.start)
        m.d.comb += self.done.eq(reg[3])


        a_tmp_real = Signal(signed(42))
        a_tmp_imag = Signal(signed(42))
        # b_tmp_real = Signal(signed(42))
        # b_tmp_imag = Signal(signed(42))

        m.d.sync1 += a_tmp_real.eq(self.a_real)
        m.d.sync1 += a_tmp_imag.eq(self.a_imag)

        # maybe this requires more intelligent clocking?
        m.d.sync1 += self.b_tmp_real.eq((self.b_real * self.tw_real) - (self.b_imag * self.tw_imag))
        m.d.sync1 += self.b_tmp_imag.eq((self.b_real * self.tw_imag) + (self.b_imag * self.tw_real))

        # paper claims this should be 20:41 and while that feels wrong it appears to be correct
        # if FFT's look like garbage consider changing
        m.d.sync3 += self.a_prime_real.eq(a_tmp_real + self.b_tmp_real[20:41])
        m.d.sync3 += self.a_prime_imag.eq(a_tmp_imag + self.b_tmp_imag[20:41])
        m.d.sync3 += self.b_prime_real.eq(a_tmp_real - self.b_tmp_real[20:41])
        m.d.sync3 += self.b_prime_imag.eq(a_tmp_imag - self.b_tmp_imag[20:41])

        return m

class FFT(Elaboratable):
    def __init__(self):
        pass

    def elaborate(self, platform: Platform) -> Module:
        m = Module()
        butterfly = Butterfly()

        start_reg = Signal(3)
        m.d.sync += start_reg.eq(start_reg + 1)
        m.d.comb += butterfly.start.eq(start_reg == 7)

        m.submodules += butterfly

        reg = Signal(10)

        m.d.sync += reg.eq(reg + 1)
        m.d.comb += butterfly.a_real.eq(reg)
        m.d.comb += butterfly.a_imag.eq(-reg)
        m.d.comb += butterfly.b_real.eq(-reg)
        m.d.comb += butterfly.b_imag.eq(reg)

        m.d.comb += butterfly.tw_real.eq(-1 * 2**20)
        m.d.comb += butterfly.tw_imag.eq(-1 * 2**20)

        return m

if __name__ == "__main__":
    top = FFT()

    main(top)
