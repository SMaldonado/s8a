from nmigen import *
from nmigen.sim import Simulator, Delay, Settle
from fft import Butterfly

import numpy as np
from math import pi
from random import randrange

if __name__ == "__main__":
    m = Module()
    m.submodules.butterfly = butterfly = Butterfly()

    sim = Simulator(m)
    sim.add_clock(1e-6) # important

    def test_butterfly():
        N = 21

        tw_max = 2**(N-1) - 1
        tw_real = tw_max
        tw_imag = tw_max
        const_tw_real = Const(tw_real)
        const_tw_imag = Const(tw_imag)
        yield butterfly.tw_real.eq(const_tw_real)
        yield butterfly.tw_imag.eq(const_tw_imag)

        failed = 0
        tests = 0

        for i in range(100):
            # produce random samples of a and b with sum of real and imaginary parts <= 2**(N-1)

            ar = randrange(2**(N-1)) - (2**(N-2))
            aimax = (2**(N-2)) - abs(ar)
            ai = randrange(2*aimax) - aimax
            br = randrange(2**(N-1)) - (2**(N-2))
            bimax = (2**(N-2)) - abs(br)
            bi = randrange(2*bimax) - bimax

            yield butterfly.a_real.eq(ar)
            yield butterfly.a_imag.eq(ai)
            yield butterfly.b_real.eq(br)
            yield butterfly.b_imag.eq(bi)
            yield
            yield butterfly.start.eq(1)
            yield
            yield butterfly.start.eq(0)

            for j in range(4):
                yield

            done = yield(butterfly.done)
            if not done:
                print('Expected done to be true; got {}'.format(done))

            gotr = yield(butterfly.a_prime_real)
            goti = yield(butterfly.a_prime_imag)
            wantr = ar + ((tw_real*br) - (tw_imag*bi)) // (2**(N-1))
            wanti = ai + ((tw_real*bi) + (tw_imag*br)) // (2**(N-1))
            b_tmp_real = yield(butterfly.b_tmp_real)
            b_tmp_imag = yield(butterfly.b_tmp_imag)
            b_tmp_real_shift = yield(butterfly.b_tmp_real_shift)
            b_tmp_imag_shift = yield(butterfly.b_tmp_imag_shift)

            if gotr != wantr or goti != wanti:
                print('Test failed for a = {} + {}j, b = {} + {}j, tw = {} + {}j;\r\n'
                      'got a\' = {} + {}j, expected a\' = {} + {}j\r\n'
                      'b_tmp = {} + {}j = {} + {}j (expected {} + {}j)'
                       .format(ar, ai, br, bi, tw_real, tw_imag, gotr, goti, wantr, wanti, b_tmp_real, b_tmp_imag, b_tmp_real_shift, b_tmp_imag_shift, br - bi, br + bi))
                print()
                failed += 1

            gotr = yield(butterfly.b_prime_real)
            goti = yield(butterfly.b_prime_imag)
            wantr = ar - ((tw_real*br) - (tw_imag*bi)) // (2**(N-1))
            wanti = ai - ((tw_real*bi) + (tw_imag*br)) // (2**(N-1))

            if gotr != wantr or goti != wanti:
                print('Test failed for a = {} + {}j, b = {} + {}j, tw = {} + {}j;\r\n'
                      'got b\' = {} + {}j, expected b\' = {} + {}j\r\n'
                      'b_tmp = {} + {}j = {} + {}j (expected {} + {}j)'
                       .format(ar, ai, br, bi, tw_real, tw_imag, gotr, goti, wantr, wanti, b_tmp_real, b_tmp_imag, b_tmp_real_shift, b_tmp_imag_shift, br - bi, br + bi))
                print()
                failed += 1

            tests += 2

        print('butterfly failed {} of {} tests'.format(failed, tests))

    sim.add_sync_process(test_butterfly, domain="sync")
    with sim.write_vcd("sim/test.vcd", "sim/test.gtkw", traces=butterfly.ports()):
        sim.run()
        # sim.run_until(20e-6, run_passive=True)
