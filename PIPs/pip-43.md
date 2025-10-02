---
pip: 43
title: Split Rewards
description: Split Block Rewards
author: Pactus Development Team <info@pactus.org>
status: Final
type: Standards Track
category: Core
discussion-no: 247
created: 2025-08-07
---

## Abstract

This PIP proposes modifying the block reward distribution mechanism to split rewards between
Validators and the Pactus Foundation.

## Motivation

To enhance sustainability and trust in the Pactus economy,
this proposal merges the existing "Foundation" and "Team & Operations" funds into the Treasury account and
modifies the block reward mechanism.
Moving forward, rewards will be split between Validators and the Treasury, according to a fixed ratio:

- 70% to Validators
- 30% to the Pactus Foundation

## Specification

With [Batch Transfer](https://pips.pactus.org/PIPs/pip-39) support,
block rewards can be split automatically between the Validator and the Foundation in a single transaction.

The new reward distribution will follow this ratio:

- **0.7** to the Validator (block proposer)
- **0.3** to the Foundation addresses

Additionally, the balances of the existing "Foundation" and "Team & Operations" accounts will be merged into
the Treasury account as follows:

1. **Foundation Account:**
   - **Address:** `pc1z2r0fmu8sg2ffa0tgrr08gnefcxl2kq7wvquf8z`
   - **Balance:** 8,400,000.194910010 PAC

2. **Team & Operations Account:**
   - **Address:** `pc1znn2qxsugfrt7j4608zvtnxf8dnz8skrxguyf45`
   - **Balance:** 3,359,999.989010000 PAC

The Pactus Foundation reward addresses are defined as follows:

```text
  1. pc1z0k5ctvn02hsxvl9t3d2efnkv2d5k46ayfddzxg
  2. pc1zrv84qnh96pmkg2sykedtz5mlu0q72st2l5c6gg
  3. pc1zuyqdsewxl4leth4rsmzhme2qxwwsvv5qvp6lfl
  4. pc1zslj5zcrsz8f83dn04yd06pjfntn8fqstxusp2q
  5. pc1z4pus6lp0nd35nqvhl0u22aquh6dh5lkq9pkx8t
  6. pc1zpjjm2vjqvcrktsxhr0d4k46u83cv2q4nrtteft
  7. pc1z524hsllxjd25n2mzjew9np9ymwte2mg3kf3jqx
  8. pc1zvnjnprk99wt6jq85saqz8ymc4n8n0utzm9gkq8
  9. pc1zzepy0rdc70eagaj0h9ypvy9nt2y8l3gyav00s8
 10. pc1zr9q4cg8zltkdndc2cadmskvptrftsghgzh8emx
 11. pc1z4zvhmkp4q6pwasea6wc2yp7vvk58wnlcqp7c08
 12. pc1zum42zls02q7hys0gyn0lkk9rhr58jylwkv8xc8
 13. pc1z4zn4z5tqa23qu0lckn0jd0n8r0l3dxynlrv5fc
 14. pc1zu9xnuwppsx57htmhkm8dah4crkv3yxuepuxvts
 15. pc1z9e22jhexznp4v3a5je2f5uhp7u2nnd8528j4u3
 16. pc1zktyzkpld8qjzw9uy32xchssh5ajkp0uhqrhuvx
 17. pc1zxcexp09alrfvdzettn6v7a9c6wxr6tgt7zu23d
 18. pc1z7zgxvg457nsevl30utyhpr5pne6l7vuwmxmu0y
 19. pc1z8vzqyr3rdw0ut89yezfs9rmzd3ju05m7t6ume9
 20. pc1z23mrkftlg6tgfh3y7pw053tlx8k7e8cuq6v4gk
 21. pc1zfwdvv7paddhz3hpj5re4tvqavklc8lcn3laqpj
 22. pc1zs29lv7gxcglsf48k9zx0gewcewh86u05v7q2jd
 23. pc1zzhvnqgklwg9x6kukkg2at5298rqwq7r3zntmcd
 24. pc1zaqt8f58zlwj6ujft8hqtlmgequxlgh53z7m2va
 25. pc1zamglslh02haafxwcnlvtmaqk2q7zy6el3ul8ty
 26. pc1z9cqfp98qzue0wyhv4eqf5sc4rphv9jz066fjkp
 27. pc1ztjzwvxx5hva8f4uneualr7w8rfgnyq2w022y6d
 28. pc1zhefja2m90z82lwg07w2l82g672x9l3gl5cuyd8
 29. pc1z4l6mxwl09rjag99e0hvayj93zagt4m3apt4ydg
 30. pc1zmww5k5xzwzapkg9hwuppvqsmgjgcf7xe8t3skn
 31. pc1zazjcm67d9gcr227s673cmzl049ey7s9eeqntcu
 32. pc1zufm93ys6xe0axcclxlw43c9ygfslggdpqakc4g
 33. pc1znup58n2karq46ulgy64l43znc538h5wnthdnr7
 34. pc1zzekctnhk7unqa6e9gw76q3csmd22r8adzth2h7
 35. pc1zwdrghnnyrymsul52c6lz9g0etn5nr7k76f0e0n
 36. pc1zs2dag7jn8szjq5rau5jacy0fcn2z20wk0xmgtf
 37. pc1zc2mqdajamhsphmaqpcc3htytverdarl99v55my
 38. pc1z2cmlxtyz4yaruggar84kelp2kakma6lt3v2wp5
 39. pc1zg9duch5lavgnrxh8p7e4vw4f4u8v45e0264f4n
 40. pc1zxayue97rjzdwrs6xe3jmzzt43r5m6z7ua0xemf
 41. pc1z2lupx42vt3ydx7gxldg7j2870rxw437zk6g270
 42. pc1z30p2aht7lyxvj0xy0s663q0x8hrf9qz2as2kte
 43. pc1z030a9vkt7nmd5qdk9m8jrgj457degeuy3yes06
 44. pc1z644fc3ftd2d5fj83ppjq0dnnetzp3u3sa4zvdn
 45. pc1z9usnds5wqgmr78dqrf8q8ce9axsj2hpj5yjhcy
 46. pc1zt3mpyy79uf4zu2pdaw09s2cgg3e0plwja0hehz
 47. pc1ze65ate4uxj9jpusfjzezs94peln8h82q4uw3mu
 48. pc1zqs0lv79xlqd68rrqc97lgt9853f2yngrwpmt0p
 49. pc1zxhw5sghlzs44aylqlpg5wzjca63f7y83dpukqp
 50. pc1zakefesc7kdveptfyv7aklxat44r0clk2tmxxmq
 51. pc1zlzws4ellhspcast96f7l6pqtzy762x08th7tgz
 52. pc1z4tdnddwmxeppa3pcaquxhq4rrc5adcx7t3qfj0
 53. pc1zmn43x36e0jcjtqqewxj50n5rjeh8sus7e9ty2j
 54. pc1zn6e3wcg7epkq36eqmupdksy7xtcezlenwhzw4s
 55. pc1ze7fwpmqv0fq3g8c2xsl2tmqh6tsgltpncgyr0j
 56. pc1z8dwn7ewj357624cugsvpcahd9z50qk5u8lv0hu
 57. pc1zzj0hcgywnh9lx3678yfg8362ap2xvw68mwp6px
 58. pc1zq2242trf7w04qp65kz8w4c8vzmnfzv4qkq5nx9
 59. pc1z433apczddfy94agee5du2c7lwgagq0r3qzpwfg
 60. pc1zanv4v6a686g56z4zppw4yfh9tzhr0vu3ex37y4
 61. pc1zw9wy204u2y5mr90ufl6zkqysyxk2mymp947dkd
 62. pc1z6nn9qxzl62c69t0wrd2e6fnf62mdsavvqv7wh9
 63. pc1zk7vz7s0ejk05x2cl7e3z04kjmgwj0lva3jzjuh
 64. pc1zc7h8x3z6etyvmxk04l9h2p5mmpvcmf6wtywvq0
 65. pc1zx6z6ymvl9lud4zes4lelrzzl70cl9tyrx92yp2
 66. pc1zsscy3xneaz6jagmzrnhwccfps7xjauzge8l8pc
 67. pc1zvvfm7l7g670vjsnup3g3z5jajhgdk8zpz6djzs
 68. pc1zl4ryxj2etw9ulv4yst9cm5fwl7g0se7j8hh9fp
 69. pc1zyj4rfns3p7uaat42rpm5hk72frss8uzu63y7ds
 70. pc1zcc9a34x6ckw6jf46e0e5emrcy5kdpvn6ahazlc
 71. pc1zgu6qxesu5ceux0582nf38vp0nmfr6a59qm8wzk
 72. pc1z20p3fkzre4ved2fkuuvfkusr3ejusgx5frt4eh
 73. pc1zqhxs703hhttk8mgjy096uxc98tz20a637alxdd
 74. pc1zqettg2qcm4kejsf39895ua8vau8j4p7j38ws3j
 75. pc1zxz5myr8evp54ces0zfdxz3ftrfx8kyunq504zl
 76. pc1zqtlu57upjzhzpkxdldj4cw8vc847pm7yvezx96
 77. pc1zhg4gc6ezpvndph964p3qd3plzupuf792jk2xxq
 78. pc1z6e4v3q2quj5kxazxck5uv8pczdkusmzquptx47
 79. pc1z67kjqzr02wcwryt3fym0td8ugt7mk7zmmzqm8d
 80. pc1zrqs39vs5l84pk4efplg6qsz5t0q70qejp47qrh
 81. pc1z3d692p24watvepg9hgm8p3f8rr28m5wxct3lhz
 82. pc1zlx8gr05vdrqcttvwhaav6npqpanzcfld8v7zw8
 83. pc1z6ceypvm6r88uqtfm7nqepwlxm03dydwucdzkas
 84. pc1zgqysx75cu8jw6v54pagtgr0qyqen0tvftxydz8
 85. pc1zcvtmzxllvkal3qk2dtk5j8cdkszgtlvqpfwsud
 86. pc1z9hy6mgtpwe8zkfhs9f6pl7rqz29ncq0xylw0qc
 87. pc1z7dteekv7007xzj7evxvjh8kuanfr3klyhkqs35
 88. pc1zv3uvz8taq66hv5rlff77nv06f6a6eww5ydfg8q
 89. pc1z8sne0w5twj6ayexyq9y9t6em0un7u4pdv0ytr7
 90. pc1zevt5r6h35eg70dygsfnffphn8hv4qx39wukvey
 91. pc1zw8zp3mm9f3723unpcfymyjms5uvpl3gp007uwg
 92. pc1zsq02f2ukn63pw4rpywksl75ku3s5kcjzh4p2cg
 93. pc1ztvxet33xzc0h52syujk0jf3wyncwn0ucp56vqy
 94. pc1zakujzs606fk049xvnuts75hll5gmkhzp3xx2gq
 95. pc1zluxwytlxaesa4mdskpjh90mqjuc5uxcsxymvtm
 96. pc1znrjpkruxcmqrwq60zlc67nz5sft7eetf9r4h40
 97. pc1zmy564huaxd4cmzgyujqe55dr3pgsg336pp4m3l
 98. pc1zre6lx6m27g9jsrdxt70a2qrtvsqsmshje9e34m
 99. pc1zphprc83wqy3xpqyequ4andeuuz22t2pdd9whg2
100. pc1zgqq766nf3782gxvrncv8cvfszdda4ss20y4e7a
```

## Actiation

This change introduces a protocol update in Pactus, increasing the protocol version to 2.
Once more than 70% of the committee supports this upgrade,
this PIP will be activated and the protocol upgraded.
After activation, the balances of the existing "Foundation" and "Team & Operations" accounts
will be transferred to the Treasury.
