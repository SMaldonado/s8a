from nmigen import *
from nmigen.sim import Simulator, Delay, Settle
from fft import Butterfly
import numpy as np

if __name__ == "__main__":
    m = Module()
    m.submodules.butterfly = butterfly = Butterfly()

    sim = Simulator(m)
    sim.add_clock(1e-6) # important

    def test_butterfly():
        tw_max = 2**20 - 1
        tw_real = tw_max
        tw_imag = tw_max
        const_tw_real = Const(tw_real)
        const_tw_imag = Const(tw_imag)
        yield butterfly.tw_real.eq(const_tw_real)
        yield butterfly.tw_imag.eq(const_tw_imag)

        for i in range(10):
            ar = i
            ai = -i
            br = i
            bi = -i
            yield butterfly.a_real.eq(ar)
            yield butterfly.a_imag.eq(ai)
            yield butterfly.b_real.eq(br)
            yield butterfly.b_imag.eq(bi)
            yield
            yield butterfly.start.eq(1)
            yield
            yield butterfly.start.eq(0)

            for j in range(3):
                yield

            gotr = yield(butterfly.a_prime_real)
            goti = yield(butterfly.a_prime_imag)
            wantr = ar + ((tw_real*br) - (tw_imag*bi)) // (2**20)
            wanti = ai + ((tw_real*bi) + (tw_imag*br)) // (2**20)

            print('{} = {} ({}), {} = {} ({})'.format(gotr, wantr, gotr==wantr, goti, wanti, goti==wanti))

    sim.add_sync_process(test_butterfly, domain="sync")
    with sim.write_vcd("sim/test.vcd", "sim/test.gtkw", traces=butterfly.ports()):
        sim.run()
        # sim.run_until(20e-6, run_passive=True)
