# Kado
A distributed lock implemented by redis

一个基于redis的分布式锁实现

基于实际项目中使用的版本拆分而来。

为什么需要分布式锁？
同一进程内不同线程的共享资源，可以通过编程语言内置的锁来解决并发问题；但是多个进程间、同一服务的多个实例间的共享资源该如何保证一致性呢？
这就需要分布式锁了。

对于分布式锁的要求：
1. 具有超时自动解锁机制，避免陷入永久锁定；
2. 具有排他性：不能解除其他实例对资源的锁定；
3. 锁状态判断与加锁操作原子化；

Environment require:
* python 3.6 +
* Redis 4.0 +

Install requirements:
```
pip install -r requirements.txt
```

Run test:
```
python -m unittest tests/test_lock.py
```
