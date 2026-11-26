import test from 'node:test';
import assert from 'node:assert/strict';
import {basket,official,convertDollars} from '../web/model.mjs';
const start=[100,100,100,100,100,100,100,100,100], end=[120,110,100,100,100,100,100,100,113];
test('starting shares and contribution points',()=>{const r=basket(start,end,[1,3,0,0,0,0,0,0]);assert.ok(Math.abs(r.change-12.5)<1e-8);assert.equal(r.shares[0],25);assert.equal(official(start,end),113);});
test('missing component and empty basket',()=>{const gap=[null,...end.slice(1)];assert.equal(basket(start,gap,[1,0,0,0,0,0,0,0]).change,null);assert.notEqual(basket(start,gap,[0,1,0,0,0,0,0,0]).change,null);assert.equal(basket(start,end,Array(8).fill(0)),null);});

test('historical dollar ratio works both directions without inflation extrapolation',()=>{assert.equal(convertDollars(100,20,100).amount,500);assert.equal(convertDollars(500,100,20).amount,100);assert.equal(convertDollars(0,20,100).amount,0);assert.throws(()=>convertDollars(100,null,100));assert.throws(()=>convertDollars(-1,20,100));});
