import database

def main():
    try:
        db = database.DatabaseService()
        print("Connected to database successfully")
        
        # Create a simplified get_transaction_stats function
        function_sql = """
DO $$
BEGIN
  IF NOT EXISTS (SELECT FROM pg_proc WHERE proname = 'get_transaction_stats') THEN
    CREATE OR REPLACE FUNCTION public.get_transaction_stats(
      p_portfolio_id UUID
    ) RETURNS JSON AS $$
    BEGIN
      RETURN (
        WITH stats AS (
          SELECT
            COUNT(*) AS total_transactions,
            COUNT(*) FILTER (WHERE transaction_type LIKE 'BUY%') AS buy_count,
            COUNT(*) FILTER (WHERE transaction_type = 'SELL') AS sell_count,
            SUM(total_amount) FILTER (WHERE transaction_type LIKE 'BUY%') AS total_buy_amount,
            SUM(total_amount) FILTER (WHERE transaction_type = 'SELL') AS total_sell_amount,
            (SELECT symbol FROM public.transactions 
             WHERE portfolio_id = p_portfolio_id 
             GROUP BY symbol 
             ORDER BY COUNT(*) DESC LIMIT 1) AS most_traded_symbol,
            (SELECT ROW_TO_JSON(t) FROM (
                SELECT id, transaction_type, symbol, shares, price_per_share, total_amount, timestamp
                FROM public.transactions
                WHERE portfolio_id = p_portfolio_id
                ORDER BY total_amount DESC
                LIMIT 1
            ) t) AS largest_transaction
          FROM public.transactions
          WHERE portfolio_id = p_portfolio_id
        )
        SELECT ROW_TO_JSON(stats) FROM stats
      );
    END;
    $$ LANGUAGE plpgsql STABLE SECURITY DEFINER;
    
    COMMENT ON FUNCTION public.get_transaction_stats IS 'Gets transaction statistics for a portfolio';
  END IF;
END
$$;
"""
        print(f"Created function SQL, length: {len(function_sql)} characters")
        
        # Execute the SQL
        result = db.supabase.sql(function_sql).execute()
        print("SQL executed successfully")
        print(result.data if hasattr(result, 'data') else result)
            
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main() 