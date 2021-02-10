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

# TODO: maybe actually store this in RAM, because as is it can take up a lot of LUTs
class TwiddleROM(Elaboratable):
    def __init__(self, k, m):
        # k is the width of frequency domain inputs and outputs
        # m is the number of address bits for the ROM (2**m entries)
        self.k = k
        self.m = m
        self.pts = 2**m

        self.real_out = Signal(signed(self.k))
        self.imag_out = Signal(signed(self.k))

    def ports(self):
        return [self.real_out, self.imag_out]

    def elaborate(self, platform: Platform) -> Module:


class Butterfly(Elaboratable):
    def __init__(self, k):
        # k is the width of frequency domain inputs and outputs

        self.k = k

        self.start = Signal()
        self.done = Signal()

        self.a_real = Signal(signed(self.k))
        self.a_imag = Signal(signed(self.k))
        self.b_real = Signal(signed(self.k))
        self.b_imag = Signal(signed(self.k))

        self.tw_real = Signal(signed(self.k))
        self.tw_imag = Signal(signed(self.k))

        self.a_prime_real = Signal(signed(self.k))
        self.a_prime_imag = Signal(signed(self.k))
        self.b_prime_real = Signal(signed(self.k))
        self.b_prime_imag = Signal(signed(self.k))

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


        a_tmp_real = Signal(signed(2*self.k))
        a_tmp_imag = Signal(signed(2*self.k))
        b_tmp_real = Signal(signed(2*self.k))
        b_tmp_imag = Signal(signed(2*self.k))

        m.d.sync1 += a_tmp_real.eq(self.a_real)
        m.d.sync1 += a_tmp_imag.eq(self.a_imag)

        # TODO: maybe this requires more intelligent clocking?
        # i.e. multiplication on sync1 and add/subtract on sync2
        m.d.sync1 += b_tmp_real.eq((self.b_real * self.tw_real) - (self.b_imag * self.tw_imag))
        m.d.sync1 += b_tmp_imag.eq((self.b_real * self.tw_imag) + (self.b_imag * self.tw_real))

        # paper claims this should be 20:41 and while that feels wrong it appears to be correct,
        # after doing a bunch of debug when writing the testbench for the butterfly function
        # if FFT's look like garbage consider changing
        m.d.sync3 += self.a_prime_real.eq(a_tmp_real + b_tmp_real[self.k-1:(2*self.k)-1])
        m.d.sync3 += self.a_prime_imag.eq(a_tmp_imag + b_tmp_imag[self.k-1:(2*self.k)-1])
        m.d.sync3 += self.b_prime_real.eq(a_tmp_real - b_tmp_real[self.k-1:(2*self.k)-1])
        m.d.sync3 += self.b_prime_imag.eq(a_tmp_imag - b_tmp_imag[self.k-1:(2*self.k)-1])

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
