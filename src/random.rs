// SPDX-License-Identifier: BSD-3-Clause
// MT19937 algorithm: Makoto Matsumoto and Takuji Nishimura, 1997–2002.
// Ported from the algorithm embedded in hb's CPython 3.13.7 _randommodule.c.
// Copyright and redistribution terms are preserved in docs/LICENSE-MT19937.
//! The unsigned integer seed and random() sequence used by hb's Python runtime.
//! This is a reproducibility generator, not a cryptographic source.

pub struct SeededRng {
    state: [u32; 624],
    index: usize,
}

impl SeededRng {
    pub fn new(seed: u64) -> Self {
        let mut rng = Self {
            state: [0; 624],
            index: 624,
        };
        rng.state[0] = 19650218;
        for i in 1..624 {
            let previous = rng.state[i - 1];
            rng.state[i] = 1812433253u32
                .wrapping_mul(previous ^ (previous >> 30))
                .wrapping_add(i as u32);
        }
        let keys = [seed as u32, (seed >> 32) as u32];
        let length = if keys[1] == 0 { 1 } else { 2 };
        let (mut i, mut j) = (1, 0);
        for _ in 0..624 {
            let previous = rng.state[i - 1];
            rng.state[i] = (rng.state[i] ^ (previous ^ (previous >> 30)).wrapping_mul(1664525))
                .wrapping_add(keys[j])
                .wrapping_add(j as u32);
            i += 1;
            j += 1;
            if i >= 624 {
                rng.state[0] = rng.state[623];
                i = 1;
            }
            if j >= length {
                j = 0;
            }
        }
        for _ in 0..623 {
            let previous = rng.state[i - 1];
            rng.state[i] = (rng.state[i] ^ (previous ^ (previous >> 30)).wrapping_mul(1566083941))
                .wrapping_sub(i as u32);
            i += 1;
            if i >= 624 {
                rng.state[0] = rng.state[623];
                i = 1;
            }
        }
        rng.state[0] = 0x80000000;
        rng
    }

    #[cfg(test)]
    fn next_u32(&mut self) -> u32 {
        if self.index >= 624 {
            for i in 0..624 {
                let y = (self.state[i] & 0x80000000) | (self.state[(i + 1) % 624] & 0x7fffffff);
                self.state[i] = self.state[(i + 397) % 624]
                    ^ (y >> 1)
                    ^ if y & 1 == 1 { 0x9908b0df } else { 0 };
            }
            self.index = 0;
        }
        let mut y = self.state[self.index];
        self.index += 1;
        y ^= y >> 11;
        y ^= (y << 7) & 0x9d2c5680;
        y ^= (y << 15) & 0xefc60000;
        y ^= y >> 18;
        y
    }

    /// MT state words and next-word index for adapters to an existing runtime.
    pub fn state(&self) -> (&[u32; 624], usize) {
        (&self.state, self.index)
    }

    #[cfg(test)]
    pub fn random(&mut self) -> f64 {
        let a = self.next_u32() >> 5;
        let b = self.next_u32() >> 6;
        (a as f64 * 67108864.0 + b as f64) / 9007199254740992.0
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn cpython_unsigned_seed_vectors() {
        // Independent CPython 3.13 integer-seed fixtures, including both words.
        for (seed, expected) in [
            (0, 0.8444218515250481),
            (1, 0.13436424411240122),
            (4294967296, 0.11299430095636409),
            (u64::MAX, 0.021825695401270107),
        ] {
            assert_eq!(SeededRng::new(seed).random(), expected);
        }
    }

    #[test]
    fn cpython_sequences_cross_twist_boundaries() {
        let indices = [0, 1, 623, 624, 625, 1248, 99999];
        let cases: [(u64, [u32; 7]); 4] = [
            (
                0,
                [
                    3626764237, 1654615998, 2390040247, 2229104038, 1244770883, 2465233080,
                    1046498085,
                ],
            ),
            (
                1,
                [
                    577090037, 2444712010, 802355090, 1360367077, 3404757168, 1032912167,
                    3726731322,
                ],
            ),
            (
                4294967296,
                [
                    485306839, 1508871100, 1921684606, 2208258976, 2815084510, 623633719, 588735641,
                ],
            ),
            (
                u64::MAX,
                [
                    93740670, 1068495656, 2799746052, 3597309115, 1388219846, 641403452, 3905414412,
                ],
            ),
        ];
        for (seed, expected) in cases {
            let mut rng = SeededRng::new(seed);
            for index in 0..100000 {
                let actual = rng.next_u32();
                if let Some(position) = indices.iter().position(|i| *i == index) {
                    assert_eq!(actual, expected[position], "seed {seed}, sample {index}");
                }
            }
        }
    }
}
