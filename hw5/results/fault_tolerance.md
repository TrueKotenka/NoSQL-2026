# Результаты проверки отказоустойчивости

| Состояние кластера | Уровень согласованности | Чтение | Запись |
|---|---|---|---|
| 3 узла UN | QUORUM | успех | ошибка |
| 3 узла UN | ALL | успех | ошибка |
| 2 UN, 1 DN | QUORUM | успех | ошибка |
| 2 UN, 1 DN | ALL | ошибка | ошибка |
| 3 узла UN после возврата | QUORUM | успех | ошибка |
| 3 узла UN после возврата | ALL | успех | ошибка |

При факторе репликации 3 уровень QUORUM требует ответы двух реплик, а ALL — всех трёх. При остановке одного узла QUORUM остаётся доступным, ALL возвращает ошибку. Неуспешная запись с ALL может быть частично применена на работающих репликах, поэтому каждая попытка использует новый event_id.

## Сообщения об ошибках

### 3 узла UN — QUORUM — запись

```text
<stdin>:4:SyntaxException: line 1:172 no viable alternative at input 'to' (...('checkout', '2026-11-11', '2026-11-11T12:00:00+0000', [failed] to...)
Consistency level set to QUORUM.
```

### 3 узла UN — ALL — запись

```text
<stdin>:4:SyntaxException: line 1:172 no viable alternative at input 'to' (...('checkout', '2026-11-11', '2026-11-11T12:00:00+0000', [failed] to...)
Consistency level set to ALL.
```

### 2 UN, 1 DN — QUORUM — запись

```text
<stdin>:4:SyntaxException: line 1:172 no viable alternative at input 'to' (...('checkout', '2026-11-11', '2026-11-11T12:00:00+0000', [failed] to...)
Consistency level set to QUORUM.
```

### 2 UN, 1 DN — ALL — чтение

```text
<stdin>:3:NoHostAvailable: ('Unable to complete the operation against any hosts', {<Host: 127.0.0.1:9042 dc1>: Unavailable('Error from server: code=1000 [Unavailable exception] message="Cannot achieve consistency level ALL" info={\'consistency\': \'ALL\', \'required_replicas\': 3, \'alive_replicas\': 2}')})
Consistency level set to ALL.
```

### 2 UN, 1 DN — ALL — запись

```text
<stdin>:4:SyntaxException: line 1:172 no viable alternative at input 'to' (...('checkout', '2026-11-11', '2026-11-11T12:00:00+0000', [failed] to...)
Consistency level set to ALL.
```

### 3 узла UN после возврата — QUORUM — запись

```text
<stdin>:4:SyntaxException: line 1:172 no viable alternative at input 'to' (...('checkout', '2026-11-11', '2026-11-11T12:00:00+0000', [failed] to...)
Consistency level set to QUORUM.
```

### 3 узла UN после возврата — ALL — запись

```text
<stdin>:4:SyntaxException: line 1:172 no viable alternative at input 'to' (...('checkout', '2026-11-11', '2026-11-11T12:00:00+0000', [failed] to...)
Consistency level set to ALL.
```

