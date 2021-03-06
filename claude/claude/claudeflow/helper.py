import tensorflow as tf
import numpy as np
import matplotlib.pyplot as plt

def QAMencoder(x,c):
    comp = tf.transpose(tf.matmul(c,tf.cast(tf.transpose(x,(1,0)),c.dtype)),(1,0))
    return tf.concat([tf.real(comp),tf.imag(comp)],axis=1)

def IQ_abs(x):
    return tf.sqrt(tf.square(x[:,0])+tf.square(x[:,1]))

def IQ_norm(x,epsilon=1e-12):
    rmean = tf.reduce_mean( tf.square( IQ_abs(x) ) )
    rsqrt = tf.rsqrt(tf.maximum(rmean, epsilon))    
    return x*rsqrt

def logBase(x,base):
    numerator = tf.log(x)
    denominator = tf.log(tf.constant(base, dtype=numerator.dtype))
    return numerator / denominator

def log10(x):
    return logBase(x,10)

def MI(softmax, X, Px):
    MI = tf.reduce_mean( logBase( tf.reduce_sum( softmax*X, axis=-1) / Px, 2) )
    return MI

def lin2dB(lin,dBtype):
    if dBtype == 'db' or dBtype == 'dB':
        fact = 0
    elif dBtype == 'dbm' or dBtype == 'dBm':
        fact = -30
    elif dBtype == 'dbu' or dBtype == 'dBu':
        fact = -60
    else:
        raise ValueError('dBtype can only be dB, dBm or dBu.')

    fact = tf.constant(fact,lin.dtype)
    ten = tf.constant(10,lin.dtype)

    return ten*log10(lin)-fact

def dB2lin(dB,dBtype):
    if dBtype == 'db' or dBtype == 'dB':
        fact = 0
    elif dBtype == 'dbm' or dBtype == 'dBm':
        fact = -30
    elif dBtype == 'dbu' or dBtype == 'dBu':
        fact = -60
    else:
        raise ValueError('dBtype can only be dB, dBm or dBu.')

    fact = tf.constant(fact,dB.dtype)
    ten = tf.constant(10,dB.dtype)

    return ten**( (dB+fact)/ten )

def create_reset_metric(metric, scope='reset_metrics', *metric_args, **metric_kwargs):
    '''
        see https://github.com/tensorflow/tensorflow/issues/4814#issuecomment-314801758
    '''
    with tf.variable_scope(scope) as scope:
        metric_op, update_op = metric(*metric_args, **metric_kwargs)
        vars = tf.contrib.framework.get_variables(scope, collection=tf.GraphKeys.LOCAL_VARIABLES)
        reset_op = tf.variables_initializer(vars)
    return metric_op, update_op, reset_op