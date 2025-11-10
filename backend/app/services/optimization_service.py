class OptimizationService:
    """Service for energy optimization operations"""
    
    @staticmethod
    def identify_peak_hours(price_df):
        """
        Identify peak pricing hours from price data.
        
        Args:
            price_df: DataFrame with 'time' and 'price' columns
            
        Returns:
            list of peak hours (formatted as "HH:00")
        """
        if price_df.empty:
            return []
        
        try:
            mean_price = price_df['price'].mean()
            std_price = price_df['price'].std()
            
            threshold = mean_price + std_price
            
            peak_hours = price_df[price_df['price'] > threshold]['time'].unique().tolist()
            
            return sorted(peak_hours)
        except Exception as e:
            return []
