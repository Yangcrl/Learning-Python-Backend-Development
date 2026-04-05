-- 原子扣减库存的Lua脚本
-- 参数1: 库存键名
-- 返回值: 剩余库存，-1表示库存不足

local stock_key = KEYS[1]
local stock = tonumber(redis.call('hget', stock_key, 'stock'))

if stock and stock > 0 then
    -- 扣减库存
    redis.call('hset', stock_key, 'stock', stock - 1)
    -- 返回剩余库存
    return stock - 1
else
    -- 库存不足
    return -1
end
